# Copyright 2022-2024 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

import json
import random
import re
import statistics
import time
from datetime import datetime

import cloudselect.utils as utils
from cloudselect.logger import logger

from ..base import CloudProvider
from .instance import AmazonInstanceGroup
from .prices import AmazonPrices


class AmazonCloud(CloudProvider):
    """
    An Amazon cloud provider wrapper
    """

    name = "aws"

    def __init__(self, **kwargs):
        self.regions = kwargs.get("regions") or ["us-east-1"]
        self.project = None
        self.ec2_client = None
        self.pricing_cli = None

        # Exponential backoff for prices API
        self.min_sleep_time = kwargs.get("min_sleep_time") or 1e-2
        self.max_retries = kwargs.get("max_retries") or 15

        # This currently has two pieces - billing and instances (different APIs)
        self._set_services(kwargs.get("cache_only", False))
        super(AmazonCloud, self).__init__()

    def prices(self):
        """
        Use the API to retrieve and return prices to cache.
        """
        if not self.has_pricing_auth:
            return self.fail_message("prices, authentication not set.")

        from botocore.exceptions import ClientError

        # Get services first - there are almost 2k! Look for compute engine
        logger.info(f"Retrieving prices for {self.name}.")

        # Keep a price that matches any region we care about
        regex = "(%s)" % "|".join(self.regions)
        logger.debug(f"Searching for region regex {regex}")

        # Keep track of how many times we've tried
        retries = 0
        next_token = None
        prices = []

        while True:
            try:
                # AWS (as of October 2023) no longer accepts an empty NextToken
                # Max results default has also decreased, so we specify max
                if not next_token:
                    response = self.pricing_cli.get_products(
                        ServiceCode="AmazonEC2", MaxResults=100
                    )
                else:
                    response = self.pricing_cli.get_products(
                        ServiceCode="AmazonEC2",
                        NextToken=next_token,
                        MaxResults=100,
                    )
            # Be generous and retry for any client error
            except ClientError as err:
                if "Rate exceeded" not in err.args[0] or retries > self.max_retries:
                    raise
                retries += 1
                sleep = self.min_sleep_time * random.randint(1, 2**retries)
                time.sleep(sleep)
                continue

            if not response.get("NextToken"):
                break

            next_token = response.get("NextToken")
            # The prices are actually string - so let's search region of interest via regex
            for pricestr in response["PriceList"]:
                if not re.search(regex, pricestr):
                    continue
                prices.append(json.loads(pricestr))
            print(f"{len(prices)} total aws prices matching {regex}...", end="\r")
        print()

        # Try to add current spot
        try:
            updated = []
            instances = self.instances()
            spot_prices = self.spot_prices(instances)
            for p in prices:
                instance_type = p["product"]["attributes"].get("instanceType")
                if not instance_type or instance_type not in spot_prices:
                    continue
                region = p["product"]["attributes"]["regionCode"]

                # Save the availability zones, and the mean across
                sps = {
                    v["AvailabilityZone"]: float(v["SpotPrice"])
                    for k, v in spot_prices[instance_type].items()
                    if k.startswith(region)
                }
                if not sps:
                    continue

                p["terms"]["SpotPrices"] = sps
                p["terms"]["SpotPrice"] = statistics.mean(list(sps.values()))
                updated.append(p)
            prices = updated

        except Exception as e:
            print(f"Issue with parsing spot prices: {e}")
            pass

        return self.load_prices(prices)

    def spot_prices(self, instances, since=None, latest=True):
        """
        Get spot prices for a set of instances and availability zones

        since can be provided as a datetime.datetime object to filter since.
        If not defined, we default to datetime.datetime.now(). If latest is False,
        we do not organize based on the latest timestamp.
        """
        from botocore.exceptions import ClientError

        # Filter down to those that support spot
        instances = [x for x in instances.data if "spot" in x["SupportedUsageClasses"]]
        names = [x["InstanceType"] for x in instances]

        # Ensure we have services (if cache_only True this won't be set)
        if not self.has_instance_auth:
            self._set_services()

        retries = 0
        prices = {} if latest else []
        next_token = ""
        now = since or datetime.now()
        print(f"Getting latest spot prices for {len(names)} instances...")
        while True:
            try:
                response = self.ec2_client.describe_spot_price_history(
                    InstanceTypes=names,
                    ProductDescriptions=["Linux/UNIX"],
                    NextToken=next_token,
                    MaxResults=1000,
                    StartTime=now,
                )
            except ClientError as err:
                if "Rate exceeded" not in err.args[0] or retries > self.max_retries:
                    raise
                retries += 1
                sleep = self.min_sleep_time * random.randint(1, 2**retries)
                time.sleep(sleep)
                continue

            if not response.get("NextToken"):
                break

            next_token = response.get("NextToken")

            # Filter down to latest price for each availability zone
            for price in response["SpotPriceHistory"]:
                instance_type = price["InstanceType"]
                zone = price["AvailabilityZone"]

                # This returns all raw data, no organizing
                if not latest:
                    prices.append(price)
                    continue

                # Organize by instance type -> availability zone
                if instance_type not in prices:
                    prices[instance_type] = {}
                if zone not in prices[instance_type]:
                    prices[instance_type][zone] = {}

                # If we already have one, determine if newer
                if "Timestamp" in prices[instance_type][zone]:
                    current = prices[instance_type][zone]["Timestamp"]
                    contender = price["Timestamp"]

                    # Only update if the contender is newer (more recent)
                    if contender > current:
                        prices[instance_type][zone] = price

                # We haven't seen this combination yet!
                else:
                    prices[instance_type][zone] = price

        # If we just want the latest list, return early
        if not latest:
            print(f"Found {len(prices)} total aws spot prices")
            return prices

        # Convert timestamp to strings
        count = 0
        for instance_type, spot_prices in prices.items():
            for zone, spot_price in spot_prices.items():
                count += 1
                prices[instance_type][zone]["Timestamp"] = str(
                    prices[instance_type][zone]["Timestamp"]
                )

        print(f"Found {count} total aws spot prices")
        return prices

    def instances(self):
        """
        Use the API to retrieve (and return) instances within a set of regions.

        We do a little extra work to add the region attribute to make it
        accessible for filtering.
        """
        if not self.has_instance_auth:
            return self.fail_message("instances, authentication not set.")

        logger.info(f"Retrieving instances for {self.name}")

        # Start with a lookup so we can attach regions
        machine_types = []
        lookup = {}

        # Get instance types by region so we have stored in metadata
        for region in self.regions:
            response = self.ec2_client.describe_instance_type_offerings(
                DryRun=False,
                LocationType="region",
                Filters=[{"Name": "location", "Values": self.regions}],
            )
            if not response["InstanceTypeOfferings"]:
                logger.warning(
                    f"No instance types found for region selection {region} - are you sure it is correct?"
                )

            # Organize by machine type for now
            for x in response["InstanceTypeOfferings"]:
                machine_types.append(x["InstanceType"])
                if x["InstanceType"] not in lookup:
                    lookup[x["InstanceType"]] = []
                lookup[x["InstanceType"]].append(region)

        # Make sure we have unique machine types
        machine_types = list(set(machine_types))

        # From what I can tell, we don't have next pages for this smaller list.
        # We can only ask in increments of 100
        instances = []
        for chunk in utils.chunks(machine_types, 100):
            response = self.ec2_client.describe_instance_types(
                DryRun=False, InstanceTypes=chunk
            )
            for new_instance in response.get("InstanceTypes", []):
                new_instance["Regions"] = lookup.get(new_instance["InstanceType"])
                instances.append(new_instance)

        # Return a wrapped set of instances
        return self.load_instances(instances)

    def load_prices(self, data):
        """
        Load prices data from json instal class
        """
        return AmazonPrices(data)

    def load_instances(self, data):
        """
        Load instance data from json.
        """
        return AmazonInstanceGroup(data)

    def _set_services(self, cache_only=False):
        """
        Connect to needed amazon clients.

        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instance_types
        """
        # Cut out early if only cache is wanted.
        if cache_only is True:
            self.has_instance_auth = False
            self.has_pricing_auth = False
            return

        import boto3

        self.ec2_client = boto3.client("ec2", region_name=self.regions[0])
        self.pricing_cli = boto3.client("pricing", region_name=self.regions[0])

        try:
            self.ec2_client.describe_instances()
            self.has_instance_auth = True
        except Exception as e:
            logger.debug(f"Unable to authenticate to Amazon Web Services EC2: {e}")
            self.has_instance_auth = False

        # Note: purposefully set to false because we don't have an API token to test
        try:
            self.pricing_cli.describe_services(ServiceCode="AmazonEC2")
            self.has_pricing_auth = True
        except Exception as e:
            logger.debug(f"Unable to authenticate to Amazon Web Services prices: {e}")
            self.has_pricing_auth = False

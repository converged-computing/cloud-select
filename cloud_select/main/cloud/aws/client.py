# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

import cloud_select.utils as utils
from cloud_select.logger import logger

from ..base import CloudProvider
from .instance import AmazonInstanceGroup
from .prices import AmazonPrices


class AmazonCloud(CloudProvider):
    """
    An Amazon cloud provider wrapper
    """

    name = "aws"

    def __init__(self, **kwargs):
        self.regions = ["us-east-1"]
        self.project = None
        self.ec2_client = None
        self.pricing_cli = None

        # This currently has two pieces - billing and instances (different APIs)
        self._set_services()
        super(AmazonCloud, self).__init__()

    def prices(self):
        """
        Use the API to retrieve and return prices to cache.
        """
        # TODO - this currently can't be finished because I don't have the right permissions.
        if not self.has_pricing_auth:
            return self.fail_message("prices, authentication not set.")

        # Get services first - there are almost 2k! Look for compute engine
        logger.info(f"Retrieving prices for {self.name}.")

        # This is how we get the service types we can ask for
        # response = self.pricing_cli.describe_services(ServiceCode="AmazonEC2")
        # And next we get the list of instance types (on the order of 600)
        next_token = ""
        instance_types = []
        while True:
            response = self.pricing_cli.get_attribute_values(
                ServiceCode="AmazonEC2",
                AttributeName="instanceType",
                NextToken=next_token,
            )
            if not response.get("NextToken"):
                break
            next_token = response.get("NextToken")
            instance_types += [x["Value"] for x in response["AttributeValues"]]
            print(f"{len(instance_types)} total instances...", end="\r")

        # Now we get prices for those
        query = [
            {"Type": "TERM_MATCH", "Field": "instanceType", "Value": x}
            for x in instance_types
        ]
        response = self.pricing_cli.get_products(ServiceCode="AmazonEC2", Filters=query)
        return self.load_prices(response)

    def instances(self):
        """
        Use the API to retrieve (and return) instances within a set of regions.
        """
        if not self.has_instance_auth:
            return self.fail_message("instances, authentication not set.")

        logger.info(f"Retrieving instances for {self.name}")

        # Get instance types in the region - give a warning if no response.
        response = self.ec2_client.describe_instance_type_offerings(
            DryRun=False,
            LocationType="region",
            Filters=[{"Name": "location", "Values": self.regions}],
        )
        if not response["InstanceTypeOfferings"]:
            logger.warning(
                f"No instance types found for region selection {self.regions} - are you sure these are correct?"
            )
            return

        # This list has (it appears unique) machine type, and location - we need to use the API to get details
        machine_types = list(
            set([x["InstanceType"] for x in response["InstanceTypeOfferings"]])
        )

        # From what I can tell, we don't have next pages for this smaller list.
        # We can only ask in increments of 100
        instances = []
        for chunk in utils.chunks(machine_types, 100):
            response = self.ec2_client.describe_instance_types(
                DryRun=False, InstanceTypes=chunk
            )
            instances += response.get("InstanceTypes", [])

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

    def _set_services(self):
        """
        Connect to needed amazon clients.

        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.describe_instance_types
        """
        import boto3

        self.ec2_client = boto3.client("ec2")
        self.pricing_cli = boto3.client("pricing")

        try:
            self.ec2_client.describe_instances()
            self.has_instance_auth = True
        except Exception as e:
            logger.warning(f"Unable to authenticate to Amazon Web Services EC2: {e}")
            self.has_instance_auth = False

        # Note: purposefully set to false because we don't have an API token to test
        try:
            self.pricing_cli.describe_services(ServiceCode="AmazonEC2")
            self.has_pricing_auth = False
        except Exception as e:
            logger.warning(f"Unable to authenticate to Amazon Web Services EC2: {e}")
            self.has_pricing_auth = False

# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

import re

import cloud_select.utils as utils
from cloud_select.logger import logger

from ..base import Instance, InstanceGroup


class AmazonInstance(Instance):

    """
    A wrapper to reveal aws instance data.

    What I haven't found yet are:
     aws is missing attribute cpu-arch (I took a guess)
     aws is missing attribute cpu-vendor (don't see intel/amd anywhere)
    """

    @property
    def name(self):
        return self.data.get("InstanceType")

    def attr_price(self):
        """
        Price of an instance, USD per hour.

        This will only be populated - a single "Price" if prices are
        enabled and present for the region.
        """
        return self.data.get("Price")

    def attr_region(self):
        """
        Return the single region
        """
        return self.data.get("Region")

    def attr_description(self):
        """
        Put together a description that looks like Google's

        "208 vCPUs, 5.75 TB RAM"
        """
        byte_value = self.attr_memory_bytes()
        if byte_value is None:
            return
        size = utils.print_bytes(byte_value)
        return f"{self.attr_cpus()} vCPUs, {size} RAM"

    def attr_gpu_memory(self):
        """
        Return GPU memory (also in MB so comparable)
        """
        if not self.attr_gpu():
            return

        # Calculate total memory
        total_mb = 0
        for gpu in self.data["GpuInfo"]["Gpus"]:
            total_mb += gpu["Count"] * gpu["MemoryInfo"]["SizeInMiB"]
        return total_mb

    def attr_gpu_vendor(self):
        """
        Return GPU vendor, if there are gpus
        """
        if not self.attr_gpu():
            return

        # Calculate total memory
        vendors = set()
        for gpu in self.data["GpuInfo"]["Gpus"]:
            vendors.add(gpu["Manufacturer"])
        return list(vendors)

    def attr_hypervisor(self):
        """
        Return hypervisor string
        """
        return self.data.get("Hypervisor")

    def attr_instance_storage(self):
        """
        Return if the instance suports storage
        """
        return self.data.get("InstanceStorageSupported")

    def attr_price_per_hour(self):
        """
        Return price per hour, if known.
        """
        return self.data.get("Price")

    def attr_gpu_model(self):
        """
        Return GPU model, if there are gpus
        """
        if not self.attr_gpu():
            return

        # Calculate total memory
        models = set()
        for gpu in self.data["GpuInfo"]["Gpus"]:
            models.add(gpu["Name"])
        return list(models)

    def attr_cpu_arch(self):
        """
        Get the CPU architecture

        I'm not sure if this should be in VCpuInfo (it's not)
        """
        # TODO not sure this is right
        return self.data.get("ProcessorInfo", {}).get("SupportedArchitectures") or None

    def attr_disk_type(self):
        """
        Return the disk type
        """
        # Storage is not supported
        if not self.attr_instance_storage():
            return
        disk_types = set()
        for disk in self.data.get("InstanceStorageInfo", {}).get("Disks", []):
            disk_type = disk.get("Type")
            if disk_type:
                disk_types.add(disk_type)
        return list(disk_types)

    def attr_cpus(self):
        """
        Number of cpus the instance has.
        """
        return self.data.get("VCpuInfo", {}).get("DefaultVCpus")

    def attr_memory(self):
        """
        Memory is in MB
        """
        return self.data.get("MemoryInfo", {}).get("SizeInMiB")

    def attr_free_tier(self):
        """
        Determine if an instance is free tier.
        """
        return self.data.get("FreeTierEligible")

    def attr_ipv6(self):
        """
        Determine if an instance can support ipv6
        """
        return self.data.get("NetworkInfo", {}).get("Ipv6Supported")

    def attr_gpu(self):
        """
        Determine if an instance can support gpu
        """
        return self.data.get("GpuInfo") and len(self.data["GpuInfo"].get("Gpus")) > 0

    def attr_gpus(self):
        """
        Determine number of gpus an instance can support.
        """
        gpus = self.data.get("GpuInfo", {}).get("Gpus")
        if not gpus:
            return
        count = 0
        for gpu_spec in gpus:
            count += gpu_spec["Count"]
        return count


class AmazonInstanceGroup(InstanceGroup):
    """
    A Google Cloud instance group.

    An instance group stores raw data, and allows for query or
    other interaction over instances.
    """

    name_attribute = "InstanceType"
    Instance = AmazonInstance

    def filter_region(self, region):
        """
        A request to filter down to a specific region regular expression.

        The solver cannot handle this.
        """
        self.data = [x for x in self.data if re.search(region, " ".join(x["Regions"]))]

    def iter_instances(self):
        """
        Amazon provides regions together, so here we yield instance data with just one region.
        """
        for item in self.data:
            regions = item.get("Regions")
            if not regions:
                yield self.Instance(item)
                continue

            # Provide finally as single region and price
            for region in regions:
                item["Region"] = region
                item["Price"] = item.get("Prices", {}).get(region)
                yield self.Instance(item)

    def add_instance_prices(self, prices):
        """
        Add pricing information to instances

        We currently are filtering to Linux, OnDemand, and USD per hour.
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/pricing.html
        """
        lookup = build_instance_price_lookup(prices.data)

        # Add prices to instances we have prices for
        for instance in self.data:

            # Set to unreasonably high so it's not a choice
            if instance["InstanceType"] in lookup:

                # Make a list of prices that matches regions
                region_prices = {}
                for region in instance["Regions"]:
                    if region in lookup[instance["InstanceType"]]:
                        region_prices[region] = lookup[instance["InstanceType"]][region]
                    instance["Prices"] = region_prices


def build_instance_price_lookup(prices):
    """
    Function to build a lookup of prices.

    We do this to make it easy for a testing function to use the same method.
    """
    lookup = {}
    for price in prices:
        if (
            "instanceType" not in price["product"]["attributes"]
            or "OnDemand" not in price["terms"]
            or price["product"]["productFamily"] != "Compute Instance"
        ):
            continue

        # I think we want BoxUsage https://docs.aws.amazon.com/cost-management/latest/userguide/ce-filtering.html
        # Note that I also see HostBoxUsage and MIA1-BoxUsage but am filtering to those that start with BoxUsage for consistency
        if price["product"]["attributes"]["operatingSystem"] != "Linux" or not price[
            "product"
        ]["attributes"]["usagetype"].startswith("BoxUsage"):
            continue

        # The operation attribute looks like:
        # operation: ['RunInstances:0004', 'RunInstances:0200', 'RunInstances:0100', 'RunInstances']
        # And we have totally identical instances except for that, but in rates the numbers correspond to "extras" like enterprise, sql, web.
        # So for now we just want to filter to vanilla "RunInstances" which looks like the raw EC2 price
        if price["product"]["attributes"]["operation"] != "RunInstances":
            continue

        # How we will organize result entries
        location = price["product"]["attributes"]["regionCode"]
        instance_type = price["product"]["attributes"]["instanceType"]

        assert len(price["terms"]["OnDemand"]) == 1
        priceid = list(price["terms"]["OnDemand"].keys())[0]
        for _, rate in price["terms"]["OnDemand"][priceid]["priceDimensions"].items():
            if rate["unit"].lower() == "hrs":
                if instance_type not in lookup:
                    lookup[instance_type] = {}
                if location in lookup[instance_type]:
                    logger.warning(
                        f"Found two rates for {instance_type} in {location} - we will choose one but this likely should not happen."
                    )
                # These are provided as strings, since the original data is completely string
                lookup[instance_type][location] = float(rate["pricePerUnit"]["USD"])
    return lookup

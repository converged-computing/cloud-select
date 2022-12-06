# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

from ..base import Instance, InstanceGroup


class AmazonInstance(Instance):
    @property
    def name(self):
        return self.data.get("InstanceType")

    def attr_cpus(self):
        """
        Number of cpus the instance has.
        """
        return self.data.get("VCpuInfo", {}).get("DefaultVCpus")

    def attr_memory(self):
        """
        Memory is in GB
        """
        mb = self.data.get("MemoryInfo", {}).get("SizeInMiB")
        if mb:
            return int(mb / 1024)

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
        return "GpuInfo" in self.data and self.data["GpuInfo"]

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

    def add_instance_prices(self, prices):
        """
        Add pricing information to instances

        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/pricing.html
        """
        print("TODO add prices")

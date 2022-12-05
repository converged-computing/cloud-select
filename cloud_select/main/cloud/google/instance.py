# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

from ..base import Instance, InstanceGroup


class GoogleCloudInstance(Instance):
    def generate_row(self):
        """
        Given an instance name, return a row with the cloud
        name and other attributes.
        """
        return {
            "cloud": "google",
            "name": self.name,
            "memory": self.attr_memory(),
            "cpus": self.attr_cpus(),
            "gpus": self.attr_gpus(),
            "description": self.attr_description(),
        }

    def attr_cpus(self):
        """
        Number of cpus the instance has.
        """
        return self.data.get("guestCpus")

    def attr_memory(self):
        """
        Memory is in GB
        """
        return int(self.data["memoryMb"] / 1024)

    def attr_free_tier(self):
        """
        Determine if an instance is free tier.
        https://cloud.google.com/free/docs/free-cloud-features#compute

        This is a best effort ESTIMATION based on the name of the instance,
        saying it _could_ be free tier but isn't necessarily if you've used
        your monthly allowance. We will want to add that preamble somewhere.
        """
        # We treat booleans as lowercase strings
        return str("micro" in self.name).lower()

    def attr_ipv6(self):
        """
        Determine if an instance can support ipv6
        As far as I can tell - they all can be configured with a subnet that does?

        https://cloud.google.com/compute/docs/ip-addresses/configure-ipv6-address
        """
        return True

    def attr_gpu(self):
        """
        Determine if an instance can support gpu

        https://cloud.google.com/compute/docs/gpus

        To run NVIDIA A100 GPUs, you must use the accelerator-optimized (A2) machine type.
        """
        accels = self.data.get("accelerators", []) or []
        return len(accels) > 1 or "gpu" in self.name.lower()

    def attr_gpus(self):
        """
        Determine number of gpus an instance can support.

        https://cloud.google.com/compute/docs/gpus

        To run NVIDIA A100 GPUs, you must use the accelerator-optimized (A2) machine type.
        """
        accels = self.data.get("accelerators", []) or []
        count = None

        # List of [{'guestAcceleratorType': 'nvidia-tesla-a100', 'guestAcceleratorCount': 8}]
        if accels:
            for accel in accels:
                found_count = accel.get("guestAcceleratorCount")
                if found_count and count is None or found_count > count:
                    count = found_count
        return count


class GoogleCloudInstanceGroup(InstanceGroup):
    """
    A Google Cloud instance group.

    An instance group stores raw data, and allows for query or
    other interaction over instances.
    """

    name_attribute = "name"
    Instance = GoogleCloudInstance

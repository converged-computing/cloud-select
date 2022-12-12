# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

import copy
import re

from cloud_select.logger import logger

from ..base import Instance, InstanceGroup


class GoogleCloudInstance(Instance):
    def attr_cpus(self):
        """
        Number of cpus the instance has.
        """
        return self.data.get("guestCpus")

    def attr_memory(self):
        """
        Memory is in MB
        """
        return self.data.get("memoryMb")

    def attr_price_per_hour(self):
        """
        Price in USD per hour.
        """
        return self.data.get("price")

    def attr_region(self):
        """
        Return the (| joined) listing of regions
        """
        return self.data.get("zone")

    def attr_free_tier(self):
        """
        Determine if an instance is free tier.
        https://cloud.google.com/free/docs/free-cloud-features#compute

        This is a best effort ESTIMATION based on the name of the instance,
        saying it _could_ be free tier but isn't necessarily if you've used
        your monthly allowance. We will want to add that preamble somewhere.
        """
        return "micro" in self.name

    def attr_ipv6(self):
        """
        Determine if an instance can support ipv6
        As far as I can tell - they all can be configured with a subnet that does?

        https://cloud.google.com/compute/docs/ip-addresses/configure-ipv6-address
        """
        return True

    def attr_price(self):
        """
        Price of an instance, USD per hour.

        This is not added for Google yet
        """
        return self.data.get("price")

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

    def filter_region(self, region):
        """
        A request to filter down to a specific region regular expression.

        The solver cannot handle this.
        """
        self.data = [x for x in self.data if re.search(region, x["zone"])]

    def add_instance_prices(self, prices):
        """
        Add pricing information to instances

        Prices have these categories:
          - {'Compute', 'License', 'Network', 'Storage'}
        And these usage types:
          - {'Commit1Mo', 'Commit1Yr', 'Commit3Yr', 'OnDemand', 'Preemptible'}

        For now we will filter to "Compute" and "OnDemand" but these could be changed.
        """
        # We currently only support prices-web.json
        if not prices.data:
            return
        if isinstance(prices.data, list):
            logger.warning("There is no support get for Google Cloud API prices.")
            return

        logger.warning(
            "Google Cloud instance prices derived from the web are limited to Iowa (us-centra-1)"
        )

        # Get actual machine types and convert web listing to types
        actual_types = set([x["name"] for x in self.data])
        lookup = {}
        for _, metadata in prices.data.items():
            meta = copy.deepcopy(metadata)
            if not meta.get("table"):
                continue
            header = meta["table"].pop(0)
            for row in meta["table"]:
                if not row:
                    continue
                if row[0] in actual_types:

                    # Find price index
                    idx = [
                        i
                        for i, x in enumerate(header)
                        if "price" in x.lower() and "spot" not in x.lower()
                    ]
                    if not idx:
                        continue
                    price = row[idx[0]]
                    lookup[row[0]] = float(price.replace("$", ""))

        # Now add to data
        for entry in self.data:
            if entry["name"] in lookup:
                entry["price"] = lookup[entry["name"]]

        # This is data from the Google Cloud API which we probably want to use.
        # data = [
        #    x
        #    for x in prices.data
        #    if x["category"]["resourceFamily"] == "Compute"
        #    and x["category"]["usageType"] == "OnDemand"
        # ]
        # TODO - here we have a lsiting with snapshot, CPU, RAM, and I suspect we will need to combine attributes to get costs
        # for instances. This is a TODO I want help with. For now, we do nothing

# Copyright 2022-2024 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

import math
import re

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

    def attr_spot_price(self):
        """
        Spot price of an instance, USD per hour.
        """
        return self.data.get("spot_price")

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

        For now we will filter to "Compute" and "OnDemand/Preemtible"
        """
        if not prices.data:
            return

        # I'm writing this out stupidly / in detail so the logic is clear.
        # Filter prices down to compute (and then separate on demand from spot) for each of CPU and memory
        data = [x for x in prices.data if x["category"]["resourceFamily"] == "Compute"]

        # Get rid of sole tenancy - it's hard to use anyway
        data = [x for x in data if "sole tenancy" not in x["description"].lower()]

        # Also get rid of AMD and reserved I'm not interested for now
        data = [
            x
            for x in data
            if not re.search("(reserved|amd|premium)", x["description"].lower())
        ]
        data = [
            x
            for x in data
            if re.search(
                "(compute optimized|instance core|ram)", x["description"].lower()
            )
        ]

        on_demand = [x for x in data if x["category"]["usageType"] == "OnDemand"]
        preemptible = [x for x in data if x["category"]["usageType"] == "Preemptible"]

        # Just organizing for myself
        on_demand_cpu = [
            x for x in on_demand if x["category"]["resourceGroup"] == "CPU"
        ]
        preemptible_cpu = [
            x for x in preemptible if x["category"]["resourceGroup"] == "CPU"
        ]

        on_demand_mem = [
            x for x in on_demand if x["category"]["resourceGroup"] == "RAM"
        ]
        preemptible_mem = [
            x for x in preemptible if x["category"]["resourceGroup"] == "RAM"
        ]

        # So... we have to use regex to match to instance types? 😕️
        # Find the instance core type based on X instance core
        on_demand_lookup = {}
        preemptible_lookup = {}
        janky_price_parsing(on_demand_cpu, "cpu", on_demand_lookup)
        janky_price_parsing(on_demand_mem, "mem", on_demand_lookup)
        janky_price_parsing(preemptible_cpu, "cpu", preemptible_lookup)
        janky_price_parsing(preemptible_mem, "mem", preemptible_lookup)

        # At this point we have lookups for each of spot / on demand, cpu and mem dollars / hour
        # Add to the data!
        for item in self.data:
            # We aren't calculating accelerators (GPU) pricing for now...
            if item.get("accelerators"):
                continue

            prefix = item["name"].split("-")[0]

            # We assume the pricing / instance data are paired
            region = item["zone"].rsplit("-", 1)[0]

            # 2 vcpu == 1 actual cpu, but I think they are doing vcpu?
            actual_cpu = item["guestCpus"]
            actual_mem_gb = item["memoryMb"] / 1000

            # This would be the price for the instance type per hour
            # Just try for both
            try:
                spot_price = (
                    actual_cpu * preemptible_lookup[prefix]["cpu"][region]
                    + actual_mem_gb * preemptible_lookup[prefix]["mem"][region]
                )
                item["spot_price"] = spot_price
            except Exception:
                pass

            try:
                demand_price = (
                    actual_cpu * on_demand_lookup[prefix]["cpu"][region]
                    + actual_mem_gb * on_demand_lookup[prefix]["mem"][region]
                )
                item["price"] = demand_price
            except Exception:
                pass


def janky_price_parsing(data, key, lookup=None):
    """
    Jankily parse the billing API output into a lookup.

    If one is provided, we update it with the key. This generates
    a lookup by instance prefix, unit (cpu/mem unit) and price/hour.
    """
    # These are special identifiers for different families
    # Custom is hard, it's just something with custom in the name...
    families = {
        "Memory-optimized": {"m1", "m2", "m3"},
        "Compute optimized": {"h3", "c2d", "c2"},
    }

    # Not in family regex
    not_in_family = "(%s)" % "|".join(list(families.keys()))

    def add_instance(instance_name, item):
        """
        Helper function to add an instance item to the lookup
        """
        if instance_name not in lookup:
            lookup[instance_name] = {}
        if key not in lookup[instance_name]:
            lookup[instance_name][key] = {}

        for region in item["serviceRegions"]:
            # See https://cloud.google.com/recommender/docs/reference/rest/Shared.Types/Money
            # We divide by 10^9 to convert nanos to USD/hour (per unit like cpu)
            nanos = item["pricingInfo"][0]["pricingExpression"]["tieredRates"][0][
                "unitPrice"
            ]["nanos"]

            # This is USD / unit (cpu or mem) / hour
            lookup[instance_name][key][region] = nanos / math.pow(10, 9)

    # Do this for each of cpu and memory
    for item in data:
        # For spot, we need to remove this prefix
        description = item["description"].replace("Spot Preemptible", "").strip()
        for family, instance_names in families.items():
            if family in description:
                for instance_name in instance_names:
                    add_instance(instance_name, item)

            # Otherwise, it's a type we can parse
            elif not re.search(not_in_family, description):
                instance_name = (
                    description.split("Instance Type")[0].strip().lower().split(" ")[0]
                )
                add_instance(instance_name, item)

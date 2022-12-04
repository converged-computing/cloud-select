# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

from ..base import Instance, InstanceGroup


class GoogleCloudInstance(Instance):
    def attr_cpus(self):
        return self.data.get("guestCpus")

    def attr_memory_gb(self):
        return self.data["memoryMb"] / 1024

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


# select(Cloud, Instance) :-
#    has_attr(Cloud, Instance, "gpu", "false"),
#    has_attr(Cloud, Instance, "memory", 4),
#    has_attr(Cloud, Instance, "free_tier", "false"),
#    has_attr(Cloud, Instance, "ipv6", "false").

#        "imageSpaceGb": 0,
#        "maximumPersistentDisks": 128,
#        "maximumPersistentDisksSizeGb": "263168",
#        "selfLink": "https://www.googleapis.com/compute/v1/projects/dinodev/zones/us-west1-a/machineTypes/t2d-standard-8",
#        "isSharedCpu": false

# TODO logic for gpus https://cloud.google.com/compute/docs/gpus


class GoogleCloudInstanceGroup(InstanceGroup):
    """
    A Google Cloud instance group.

    An instance group stores raw data, and allows for query or
    other interaction over instances.
    """

    Instance = GoogleCloudInstance

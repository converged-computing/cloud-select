# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

from cloud_select.logger import logger


class Properties:
    """
    Properties from a schema to go into a solve.
    """

    # Do not go into the solve (but if defined, used before or after)
    not_solver_properties = ["include_list", "exclude_list"]

    # expected to have <name>, <name>_min, <name>_max
    range_properties = [
        "cpus",
        "instance_storage",
        "memory",
        "gpu_memory",
        "price_per_hour",
    ]

    def __init__(self, properties, **kwargs):
        self._allowed = properties
        self.set_properties(**kwargs)

    def set_properties(self, **kwargs):
        """
        Given an unknown set of command line arguments, parse into known
        instance properties. This resets properties / defined on the instance.

        We assume that properties coming from argumnts might have a "-" instead of _.
        """
        properties = {
            k: v for k, v in kwargs.items() if k.replace("_", "-") in self._allowed
        }
        # Instance level properties (to be deleted from selection, used separately)
        self.set_non_solver_properties(properties)

        # The user is asking for these defined
        self.defined = {k: v for k, v in properties.items() if v is not None}

        # GPU is handled specially since there is a boolean and min/max/number
        self.set_gpu_properties()

        # Here we need custom handling of min / max ranges. E.g., if a single value is
        # provided, we look exactly for that. If a min or max is provided, we look for
        # the range.
        self.set_range_properties()

    def set_range_properties(self):
        """
        Consolidate range into either min/max or one value.
        """
        for prop in self.range_properties:
            self._set_range_properties(prop)

    def _set_range_properties(self, prop):
        """
        Set range properties for one property in defined.
        """
        # Case 1: explicitly asking for a number - honor it.
        range_props = [f"{prop}_min", f"{prop}_max"]
        if prop in self.defined:
            for range_prop in range_props:
                if range_prop in self.defined:
                    del self.defined[range_prop]
            return

        # Case 2: Min and/or max is set - we have a range
        values = {"min": None, "max": None}
        for range_prop in range_props:
            if range_prop in self.defined:
                value = self.defined[range_prop]

                # Sanity check - always >= 0
                if value and value < 0:
                    logger.exit(f"Found {range_prop} value < 0: {value}.")

                values[range_prop.replace(f"{prop}_", "")] = value
                del self.defined[range_prop]

        # If we have min and max, assert max >= min
        if values["min"] is not None and values["max"] is not None:
            if values["max"] < values["min"]:
                logger.exit(
                    f"Found max {values['max']} less than a min {values['min']}, invalid."
                )

        # Only add if we've found a min and/or max
        if values["min"] is not None or values["max"] is not None:
            self.defined[f"range:{prop}"] = values

    def set_gpu_properties(self):
        """
        Parse desired properties into single GPU request.
        There is both a min/max/number specification and a general flag.
        """
        # Properties that ask for a specific count
        gpu_props = ["gpus", "gpus_max", "gpus_min"]

        # Case 1: they just provided the "I want gpu don't care the details" flag
        if "gpu" in self.defined and not any(x for x in gpu_props if x in self.defined):
            return

        # Case 2: they provided the gpu flag but have other specs, delete GPU flag
        if "gpu" in self.defined:
            del self.defined["gpu"]

        # Case 3: Just a gpus is set (exact number) delete the rest
        self._set_range_properties("gpus")

    def set_non_solver_properties(self, properties):
        """
        These properties are used later (e.g., to filter a final set based on name).
        """
        # Instance level properties (to be deleted from selection, used separately)
        for prop in self.not_solver_properties:
            if prop not in properties:
                setattr(self, prop, None)
                continue
            setattr(self, prop, properties.get(prop))
            del properties[prop]

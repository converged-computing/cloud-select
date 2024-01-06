# Copyright 2022-2024 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

## ContainerConfig Schema

import cloudselect.defaults as defaults

schema_url = "http://json-schema.org/draft-07/schema"

# This is also for latest, and a list of tags

# The simplest form of aliases is key/value pairs
keyvals = {
    "type": "object",
    "patternProperties": {
        "\\w[\\w-]*": {"type": "string"},
    },
}

instance_properties = {
    "gpus": {
        "type": "integer",
        "description": "Number of gpus needed (assumes gpu-enabled wanted) and sets gpu min and max to the same value.",
    },
    "gpus-min": {
        "type": "integer",
        "description": "Min of total number of GPUs (e.g., 4) if --gpus-max not set, is infinity",
    },
    "gpus-max": {
        "type": "integer",
        "description": "Max of total number of GPUs (e.g., 4) if --gpus-min not set, it is 0",
    },
    "gpu": {"type": "boolean", "description": "GPU-enabled instance type."},
    "gpu-memory": {
        "type": "integer",
        "description": "Total memory across GPUs in GiB (e.g., 4) sets --gpu-memory-min and --gpu-memory-max to the same value",
    },
    "gpu-memory-min": {
        "type": "integer",
        "description": "Min of total memory across GPUs in GiB (e.g., 4 GiB) if --gpu-memory-max not set, is infinity",
    },
    "gpu-memory-max": {
        "type": "integer",
        "description": "Max of total memory across GPUs in GiB (e.g., 4 GiB) if --gpu-memory-min not set, it is 0",
    },
    "gpu-model": {"type": "string", "description": "GPU model name."},
    "region": {
        "type": "string",
        "description": "Regular expression or string to search for in region name.",
    },
    "hypervisor": {
        "type": "string",
        "description": "Hypervisor.",
        "enum": ["xen", "nitro"],
    },
    "memory": {
        "type": "integer",
        "description": "Total memory needed and sets memory min and max to the same value.",
    },
    "memory-min": {
        "type": "integer",
        "description": "Min memory needed in GiB. if max not set, is infinity",
    },
    "memory-max": {
        "type": "integer",
        "description": "Max memory needed in GiB if min not set, it is 0",
    },
    "instance-storage": {
        "type": "integer",
        "description": "Amount of local instance storage in GiB. Sets --instance-storage-min and -max to the same value.",
    },
    "instance-storage-min": {
        "type": "integer",
        "description": "Minimum amount of local instance storage in GiB. If --instance-storage-max not set, is infinity.",
    },
    "instance-storage-max": {
        "type": "integer",
        "description": "Maximum amount of local instance storage in GiB. If --instance-storage-min not set, is 0.",
    },
    "cpus": {
        "type": "integer",
        "description": "Number of vcpus available to the instance type. Sets min and -max to the same value.",
    },
    "cpus-min": {
        "type": "integer",
        "description": "Minimum number of vcpus available to the instance type. If max not set, is infinity.",
    },
    "cpus-max": {
        "type": "integer",
        "description": "Maximum number of vcpus available to the instance type. If min not set, is 0.",
    },
    # It seems unlikely to find an exact price, but might as well be consistent!
    "price": {
        "type": "number",
        "description": "Price/hour in dollars (e.g., 0.09) (sets min and max to the same value)",
    },
    "price-min": {
        "type": "number",
        "description": "Minimum price/hour in dollars. If max not set, is infinity.",
    },
    "price-max": {
        "type": "number",
        "description": "Maximum price/hour in dollars. If min not set, is 0.",
    },
    "spot-price": {
        "type": "number",
        "description": "Price/hour for spot in dollars (e.g., 0.09) (sets min and max to the same value)",
    },
    "spot-price-min": {
        "type": "number",
        "description": "Minimum spot price/hour in dollars. If max not set, is infinity.",
    },
    "spot-price-max": {
        "type": "number",
        "description": "Maximum spot price/hour in dollars. If min not set, is 0.",
    },
    "free-tier": {"type": "boolean", "description": "Free tier only."},
    "ipv6": {"type": "boolean", "description": "Instance Types that support IPv6"},
    "cpu-arch": {
        "type": "string",
        "description": "architecture of the CPU",
        "enum": ["x86_64/amd64", "x86_64_mac", "i386", "arm64"],
    },
    "cpu-vendor": {
        "type": "string",
        "description": "manufacturer of CPU",
        "enum": ["amd", "intel", "aws"],
    },
    "gpu-vendor": {"type": "string", "enum": ["AMD", "Habana", "NVIDIA"]},
    "disk-type": {
        "type": "string",
        "description": "type of disk, hard disk or solid state",
        "enum": ["hdd", "ssd"],
    },
    "efa": {
        "type": "boolean",
        "description": "Ask for an instance that supports efa networking",
    },
    "exclude-list": {
        "type": "array",
        "items": {"type": "string"},
        "description": "instance types which should be excluded w/ regex syntax (Example: m[1-2]\.*)",  # noqa
    },
    "include-list": {
        "type": "array",
        "items": {"type": "string"},
        "description": "instance types which should be included w/ regex syntax (Example: m[1-2]\.*)",  # noqa
    },
}

## Settings.yml (loads as json)

cloud_properties = {"regions": {"type": "array", "items": {"type": "string"}}}

# Currently all of these are required
settings_properties = {
    "cache_dir": {"type": "string"},
    "config_editor": {"type": "string"},
    "cache_only": {"type": "boolean"},
    "cache_oras": {"type": "string"},
    "allow_missing_attributes": {"type": "boolean"},
    "aws": {
        "type": "object",
        "properties": cloud_properties,
        "additionalProperties": False,
        "required": ["regions"],
    },
    "google": {"type": "object", "properties": cloud_properties},
    "disable_prices": {
        "type": "boolean",
        "description": "Do not add prices as variable.",
        "default": False,
    },
    "sort-by": {
        "type": "string",
        "description": "Sort by an attribute of interest.",
        "enum": defaults.sort_by_fields,
    },
    "max-results": {
        "type": "number",
        "description": "Maximum results to return per cloud provider.",
        "default": 20,
    },
    "instances": {
        "type": "object",
        "properties": instance_properties,
        "additionalProperties": False,
    },
    "clouds": {"type": "array", "items": {"type": "string", "enum": ["google", "aws"]}},
}

settings = {
    "$schema": schema_url,
    "title": "Settings Schema",
    "type": "object",
    "required": [
        "allow_missing_attributes",
        "clouds",
        "google",
        "aws",
    ],
    "properties": settings_properties,
    "additionalProperties": False,
}

# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

## ContainerConfig Schema

import cloud_select.defaults as defaults

schema_url = "http://json-schema.org/draft-07/schema"

# This is also for latest, and a list of tags

# The simplest form of aliases is key/value pairs
keyvals = {
    "type": "object",
    "patternProperties": {
        "\\w[\\w-]*": {"type": "string"},
    },
}

# instance_properties
# This is a shared list of attributes that could be defined (and shared across clouds)
# TODO could we do some mapping of zones to generic regions (e.g., east/central/west)

# Things that need common mapping:
# - architecture
# - cpus/cores (ranges)?

# We need (in clingo facts) ways to compare things

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
    "price-per-hour": {
        "type": "number",
        "description": "Price/hour in dollars (e.g., 0.09) (sets min and max to the same value)",
    },
    "price-per-hour-min": {
        "type": "number",
        "description": "Minimum price/hour in dollars. If max not set, is infinity.",
    },
    "price-per-hour-max": {
        "type": "number",
        "description": "Maximum price/hour in dollars. If min not set, is 0.",
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
    "gpu-vendor": {"type": "string", "enum": ["nvidia"]},
    "disk-type": {
        "type": "string",
        "description": "type of disk, hard disk or solid state",
        "enum": ["hdd", "ssd"],
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

# These are not added yet (and available for AWS) if we want to add them
#      --network-encryption                             Instance Types that support automatic network encryption in-transit
#      --network-interfaces int                         Number of network interfaces (ENIs) that can be attached to the instance (sets --network-interfaces-min and -max to the same value)
#      --network-interfaces-max int                     Maximum Number of network interfaces (ENIs) that can be attached to the instance If --network-interfaces-min is not specified, the lower bound will be 0
#      --network-interfaces-min int                     Minimum Number of network interfaces (ENIs) that can be attached to the instance If --network-interfaces-max is not specified, the upper bound will be infinity
#      --network-performance int                        Bandwidth in Gib/s of network performance (Example: 100) (sets --network-performance-min and -max to the same value)
#      --network-performance-max int                    Maximum Bandwidth in Gib/s of network performance (Example: 100) If --network-performance-min is not specified, the lower bound will be 0
#      --network-performance-min int                    Minimum Bandwidth in Gib/s of network performance (Example: 100) If --network-performance-max is not specified, the upper bound will be infinity
#      --nvme                                           EBS or local instance storage where NVME is supported or required
#      --placement-group-strategy string                Placement group strategy: [cluster, partition, spread]
#  -u, --usage-class string                             Usage class: [spot or on-demand]
#      --virtualization-type string                     Virtualization Type supported: [hvm or pv]
#  -o, --output string           Specify the output format (table, table-wide, one-line, interactive)
#      --profile string          AWS CLI profile to use for credentials and config
#  -r, --region string           AWS Region to use for API requests (NOTE: if not passed in, uses AWS SDK default precedence)
#      --sort-by string          Specify the field to sort by. Quantity flags present in this CLI (memory, gpus, etc.) or a JSON path to the appropriate instance type field (Ex: ".MemoryInfo.SizeInMiB") is acceptable. (default ".InstanceType")
#      --sort-direction string   Specify the direction to sort in (ascending, asc, descending, desc) (default "ascending")

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

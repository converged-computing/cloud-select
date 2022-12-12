# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

__version__ = "0.0.12"
AUTHOR = "Vanessa Sochat"
EMAIL = "vsoch@users.noreply.github.com"
NAME = "cloud-select-tool"
PACKAGE_URL = "https://github.com/converged-computing/cloud-select"
KEYWORDS = "cloud, cost, hpc"
DESCRIPTION = "Tool for calculating costs and needs between cloud and HPC."
LICENSE = "LICENSE"

################################################################################
# Global requirements

# Since we assume wanting Singularity and lmod, we require spython and Jinja2

INSTALL_REQUIRES = (
    ("ruamel.yaml", {"min_version": None}),
    ("jsonschema", {"min_version": None}),
    ("rich", {"min_version": None}),
    ("oras", {"min_version": None}),
    ("requests", {"min_version": None}),
)

AWS_REQUIRES = (("boto3", {"min_version": None}),)

# Prefer discovery clients - more control
GOOGLE_CLOUD_REQUIRES = (
    ("google-auth", {"min_version": None}),
    ("google-api-python-client", {"min_version": None}),
)

TESTS_REQUIRES = (("pytest", {"min_version": "4.6.2"}),)

################################################################################
# Submodule Requirements (versions that include database)

INSTALL_REQUIRES_ALL = (
    INSTALL_REQUIRES + GOOGLE_CLOUD_REQUIRES + AWS_REQUIRES + TESTS_REQUIRES
)

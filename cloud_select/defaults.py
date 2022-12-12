# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)


import os

import cloud_select.utils as utils

install_dir = utils.get_installdir()
reps = {"$install_dir": install_dir, "$root_dir": os.path.dirname(install_dir)}

# The default settings file in the install root
default_settings_file = os.path.join(reps["$install_dir"], "settings.yml")

# User home
userhome = os.path.expanduser("~/.cloud-select")

# The user settings file can be created to over-ride default
user_settings_file = os.path.join(userhome, "settings.yml")
cache_dir = os.path.join(userhome, "cache")
cache_expire = 128  # one week is 128 hours

# Fields and arguments for client
sort_by_fields = ["name", "memory", "cpus", "gpus", "price"]
table_descriptors = {"price": "*Price in USD/hour"}

# variables in settings that allow environment variable expansion
allowed_envars = ["HOME"]

# ORAS annotations (we could do better here)
default_manifest_annotations = {"tool": "cloud-select"}
default_config_annotations = {"tool": "cloud-select"}
default_media_type = "org.llnl.gov.cloud-select.cloud.data"

# The default GitHub registry with recipes (for docgen)
github_url = "https://github.com/converged-computing/cloud-select"

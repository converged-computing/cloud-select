#!/usr/bin/python

# Copyright (C) 2022 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import shlex
import shutil

from cloud_select.client import get_parser
from cloud_select.main.client import Client

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)


def parse_args(argstr):
    """
    Given an argument string for a test, parse it.
    """
    parser = get_parser()
    args = parser.parse_args(shlex.split(argstr))
    args.debug = True
    return args


def init_client(tmpdir, cloud=None):
    """
    Get a common client for some container technology and module system
    """
    clouds = [cloud] if cloud else None
    settings_file = os.path.join(root, "settings.yml")
    new_settings = os.path.join(tmpdir, "settings.yml")
    new_cache = os.path.join(tmpdir, "cache")
    shutil.copyfile(settings_file, new_settings)
    client = Client(
        quiet=False,
        settings_file=new_settings,
        cache_dir=new_cache,
        clouds=clouds,
    )
    return client

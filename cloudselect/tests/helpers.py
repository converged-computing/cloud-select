#!/usr/bin/python

# Copyright (C) 2022-2023 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import shlex
import shutil

from cloudselect.client import get_parser
from cloudselect.main.client import Client

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)


def parse_args(argstr):
    """
    Given an argument string for a test, parse it.
    """
    parser = get_parser()
    parser.prog = "cloud-select"
    args = parser.parse_args(shlex.split(argstr))
    args.debug = True
    return args


def get_settings(tmpdir):
    """
    Create a temporary settings file
    """
    settings_file = os.path.join(root, "settings.yml")
    new_settings = os.path.join(tmpdir, "settings.yml")
    shutil.copyfile(settings_file, new_settings)
    return new_settings


def init_client(tmpdir, cloud=None):
    """
    Get a common client for some container technology and module system
    """
    clouds = [cloud] if cloud else None
    new_settings = get_settings(tmpdir)
    new_cache = os.path.join(tmpdir, "cache")
    client = Client(
        quiet=False,
        settings_file=new_settings,
        cache_dir=new_cache,
        clouds=clouds,
    )
    return client

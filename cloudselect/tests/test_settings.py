#!/usr/bin/python

# Copyright 2022-2023 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

import os

import pytest

from cloudselect.main.settings import Settings

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)

from .helpers import get_settings  # noqa


def test_invalid_properties(tmp_path):
    """
    Test invalid setting property
    """
    settings = Settings(get_settings(tmp_path))
    assert settings.config_editor == "vim"
    settings.set("config_editor", "code")
    with pytest.raises(SystemExit):
        settings.set("invalid_key", "invalid_value")
    assert settings.config_editor == "code"


def test_set_get(tmp_path):
    """
    Test variable set/get
    """
    settings = Settings(get_settings(tmp_path))

    assert settings.cache_only in [True, False]
    assert settings.cache_oras.endswith("nightly")
    settings.set("cache_only", True)

    regions = settings.get("google:regions")
    assert isinstance(regions, list)
    assert "us-east1" in regions

    # Just check the first in the list
    assert settings.google["regions"][0] == regions[0]
    assert settings.get("google:regions")[0] == regions[0]
    assert settings.get("google")["regions"][0] == regions[0]

#!/usr/bin/python

# Copyright 2022-2023 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

import pytest

import cloudselect.main.selectors as selectors


@pytest.mark.parametrize(
    "cloud,resources",
    [
        ("aws", {"memory_min": 4000, "memory_max": 4500, "cpus_min": 1, "cpus_max": 3}),
        (
            "google",
            {"memory_min": 4000, "memory_max": 4500, "cpus_min": 1, "cpus_max": 3},
        ),
    ],
)
def test_selector(tmp_path, cloud, resources):
    """
    Test our selector (non-interactive)
    """
    selector = selectors.InstanceSelector(cloud=cloud)
    instances = selector.select_instance(resources, interactive=False)
    assert len(instances) > 10
    assert instances[0]["price"] < instances[-1]["price"]

    # Ensure each without our range!
    for instance in instances:
        assert instance["memory"] <= resources["memory_max"]
        assert instance["memory"] >= resources["memory_min"]
        assert instance["cpus"] <= resources["cpus_max"]
        assert instance["cpus"] >= resources["cpus_min"]

    # An impossible choice without an answer returns None
    resources["memory_min"] = 999999999999998
    resources["memory_max"] = 999999999999999
    instances = selector.select_instance(resources, interactive=False)
    assert not instances

    # or the default
    instances = selector.select_instance(
        resources, default="pizza-machine", interactive=False
    )
    assert instances == "pizza-machine"

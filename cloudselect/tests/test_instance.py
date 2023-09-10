#!/usr/bin/python

# Copyright 2022-2023 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

import copy
import os

import oras.utils as utils
import pytest

import cloudselect.cloud.base as base
import cloudselect.main.schemas as schemas

from .helpers import here, init_client, parse_args

# Save small samples of data here to check against
testdata = os.path.join(here, "testdata")


@pytest.mark.parametrize(
    "cloud,min_instances,name_attribute,min_prices",
    [
        ("aws", 600, "InstanceType", 57000),
        # Web table has ~44, API data has ~2100
        ("google", 1460, "name", 40),
    ],
)
def test_instance_command(tmp_path, cloud, min_instances, name_attribute, min_prices):
    """
    Test instance commands. We put tests that use data under this function
    to be conservative about download and populating the cache from GitHub
    packages. It would probably be okay, it just takes a little bit of time.
    Instance sample data (for prices/instances) was generated on 12/11/2022
    as follows:

    import random
    random.shuffle(group.data)
    sample = random.sample(group.data, 100)
    outfile = os.path.join(testdata, f"{cloud}-{group_name}-sample.json")
    utils.write_json(sample, outfile)

    # Note that I did some manual shuffling to ensure that the instances
    # we selected for aws were also in the prices, since there are a lot.
    """
    client = init_client(str(tmp_path), cloud=cloud)

    # get clouds should add the cloud class
    assert not client._clouds
    client.get_clouds()
    assert cloud in client._clouds
    assert len(client._clouds) == 1

    # First ensure we get data! This triggers oras to get data.
    # We have a custom price file name for Google since we are
    # storing the web scraped data in the cache
    instance_cache_file = client.cache.get_cache_name(cloud, "instances")
    price_cache_file = client.cache.get_cache_name(cloud, "prices")

    # Oras should download these selectively
    assert not os.path.exists(price_cache_file)
    assert not os.path.exists(instance_cache_file)
    instances = client.update_from_cache(client.instances(), "instances")

    # This will fail if oras download failed
    os.listdir(os.path.join(client.cache.cache_dir, cloud))
    assert os.path.exists(instance_cache_file)
    assert not os.path.exists(price_cache_file)

    print(f"{cloud} instances: {len(instances[cloud].data)}")
    assert len(instances[cloud].data) > min_instances

    # Easier to interact with
    instances = instances[cloud]
    assert isinstance(instances, base.InstanceGroup)

    # Get an instance to interact with
    single_instance = instances.Instance(instances.data[0])
    assert isinstance(single_instance, base.Instance)

    # Check name attribute
    assert instances.name_attribute == name_attribute
    assert single_instance.data[name_attribute] == single_instance.name

    # Now get prices
    prices = client.update_from_cache(client.prices(), "prices")
    assert os.path.exists(price_cache_file)

    print(f"{cloud} prices: {len(prices[cloud].data)}")
    assert len(prices[cloud].data) > min_prices
    prices = prices[cloud]

    # Test region filtering
    instances.filter_region("not-exist")
    assert len(instances.data) == 0


@pytest.mark.parametrize(
    "cloud,prices_file,instances_file,region",
    [
        ("aws", "aws-prices-sample.json", "aws-instances-sample.json", "us-east-1"),
        (
            "google",
            "google-prices-sample.json",
            "google-instances-sample.json",
            "us-east1",
        ),
    ],
)
def test_instance_filters(tmp_path, cloud, prices_file, instances_file, region):
    """ """
    client = init_client(str(tmp_path), cloud=cloud)

    # Test attributes against test data
    # This ensures when we switch the format of Google price data we are aware of it
    prices_sample = utils.read_json(os.path.join(testdata, prices_file))
    instances_sample = utils.read_json(os.path.join(testdata, instances_file))

    # Set cache data to memory cache (a copy so we can edit it)
    def reset_data():
        client.cache.memory_set(cloud, copy.deepcopy(prices_sample), "prices")
        client.cache.memory_set(cloud, copy.deepcopy(instances_sample), "instances")

    reset_data()

    # Only use the cache, and don't require prices for first round
    client.settings.cache_only = True
    client.settings.disable_prices = True

    # cloud group class of instances
    instances = client.instances()[cloud]

    # Initial query - no filter arguments should return total data
    args = parse_args("")
    selection = client.instance_select(**args.__dict__)

    # no fitler should be all instances
    # this is only the case currently for aws
    # we don't add enough metadata returned from
    # the selection so they are unique (bug)
    if cloud == "aws":
        assert len(selection) == len(instances_sample)

    # We shouldn't have any prices yet
    for item in selection:
        assert not item.get("price")

    # These are parsed after the fact
    skips = ["include-list", "exclude-list"]

    # These are the ones we allow to skip for now
    # TODO need to define most for google
    google_missing = [
        "gpu-memory",
        "gpu-model",
        "hypervisor",
        "instance-storage",
        "price-per-hour",
        "cpu-arch",
        "cpu-vendor",
        "gpu-vendor",
        "disk-type",
        "efa",
    ]
    not_defined = {"aws": ["cpu-vendor"], "google": google_missing}

    # Test args for each property - not min and max (will be tested separately)
    for prop, _ in schemas.instance_properties.items():
        # Skip min and max for now - will be tested separately
        if "min" in prop or "max" in prop or prop in skips:
            continue

        # Command line args use "-" and functions use "_"
        if not instances.Instance.has_attribute(prop):
            print(f"{cloud} is missing attribute {prop}")
            if prop not in not_defined[cloud]:
                raise ValueError(f"A function for property {prop} should be defined.")

    # Turning on prices makes the set smaller
    client.settings.disable_prices = False
    reset_data()

    # Test query for our region (this shouldn't filter any out)
    instances.filter_region(region)
    if cloud == "aws":
        assert len(instances.data) == len(instances_sample)


@pytest.mark.parametrize(
    "cloud",
    [
        ("aws"),
    ],
)
def test_aws_instance_filters(tmp_path, cloud):
    """
    Test AWS filters with the client
    """
    client = init_client(str(tmp_path), cloud=cloud)
    client.settings.cache_only = True

    # Test attributes against test data
    # This ensures when we switch the format of Google price data we are aware of it
    prices_sample = utils.read_json(os.path.join(testdata, "aws-prices-sample.json"))
    instances_sample = utils.read_json(
        os.path.join(testdata, "aws-instances-sample.json")
    )

    # Set cache data to memory cache (a copy so we can edit it)
    def reset_data():
        client.cache.memory_set(cloud, copy.deepcopy(prices_sample), "prices")
        client.cache.memory_set(cloud, copy.deepcopy(instances_sample), "instances")

    reset_data()

    # Argparsing examples for filters
    # No query args mean all instances we have
    args = parse_args("instance")
    results = client.instance_select(**args.__dict__)
    assert len(results) == 100

    # Ensure each result has all data
    for attr in [
        "cloud",
        "name",
        "memory",
        "price",
        "cpus",
        "gpus",
        "region",
        "description",
    ]:
        for result in results:
            assert attr in result

    # Note that --max-results is handled by the client directly
    args = parse_args("instance --price-per-hour-min 1.0")
    results = client.instance_select(**args.__dict__)
    assert len(results) == 9
    for result in results:
        assert result["price"] >= 1.0

    args = parse_args("instance --price-per-hour-max 2.0")
    results = client.instance_select(**args.__dict__)
    assert len(results) == 13
    for result in results:
        assert result["price"] <= 2.0

    args = parse_args("instance --price-per-hour-min 1.0 --price-per-hour-max 2.0")
    results = client.instance_select(**args.__dict__)
    assert len(results) == 3
    for result in results:
        assert result["price"] <= 2.0
        assert result["price"] >= 1.0

    # Check gpu logic - the gpu flag should not take preference
    args = parse_args("instance --gpu")
    results = client.instance_select(**args.__dict__)
    assert len(results) == 6
    for result in results:
        assert result["gpus"] > 0

    args = parse_args("instance --gpus 4")
    results = client.instance_select(**args.__dict__)
    assert len(results) == 1
    assert results[0]["gpus"] == 4

    for q in [
        "instance --gpus-min 1 --gpus-max 8",
        "instance --gpus-min 1 --gpus-max 8 --gpu",
    ]:
        args = parse_args(q)
        results = client.instance_select(**args.__dict__)
        assert len(results) == 6
        for result in results:
            assert result["gpus"] >= 1
            assert result["gpus"] <= 8

    # Note that sorting and fitlering of fields missing is done by table class
    args = parse_args("instance --memory 1024")
    results = client.instance_select(**args.__dict__)
    assert len(results) == 2
    for result in results:
        assert result["memory"] == 1024


def test_interactive_database_aws(tmp_path):
    """
    Test interactive database querying with aws

    We can write a Google Cloud function when we have more
    attributes that are available.
    """
    cloud = "aws"
    client = init_client(str(tmp_path), cloud=cloud)
    client.settings.cache_only = True

    # Test attributes against test data
    # This ensures when we switch the format of Google price data we are aware of it
    prices_sample = utils.read_json(os.path.join(testdata, "aws-prices-sample.json"))
    instances_sample = utils.read_json(
        os.path.join(testdata, "aws-instances-sample.json")
    )

    # Set cache data to memory cache (a copy so we can edit it)
    def reset_data():
        client.cache.memory_set(cloud, copy.deepcopy(prices_sample), "prices")
        client.cache.memory_set(cloud, copy.deepcopy(instances_sample), "instances")

    reset_data()

    db = client.prepare_database().db
    attributes = db.execute("SELECT DISTINCT attribute from instances")
    attributes = [x[0] for x in attributes]
    for expected in [
        "cpu_arch",
        "cpus",
        "description",
        "disk_type",
        "free_tier",
        "hypervisor",
        "instance_storage",
        "ipv6",
        "memory",
        "memory_bytes",
        "price",
        "price_per_hour",
        "region",
        "gpu",
        "gpu_memory",
        "gpu_model",
        "gpu_vendor",
        "gpus",
    ]:
        assert expected in attributes

    # We shouldn't have google sneaking in here
    aws_instances = db.execute("SELECT * from instances where cloud = 'aws'")
    all_instances = db.execute("SELECT * from instances")
    assert len(all_instances) == len(aws_instances)

    results = db.execute("SELECT * from instances where instance = 'i3.8xlarge'")
    assert len(results) >= 11

    results = db.execute(
        "SELECT * from instances where attribute = 'region' and value NOT NULL AND value = 'us-east-1'"
    )
    assert len(results) == 100

    results = db.execute(
        "SELECT * from instances where attribute = 'gpu' and value_bool NOT NULL AND value_bool = 1"
    )
    assert len(results) == 6

    results = db.execute(
        "SELECT * from instances where attribute = 'gpus' and value_number NOT NULL AND value_number = 4"
    )
    assert len(results) == 1

    results = db.execute(
        "SELECT * from instances where attribute = 'gpus' and value_number NOT NULL AND value_number > 6 and value_number < 10"
    )
    assert len(results) == 2

    results = db.execute(
        "SELECT DISTINCT instance from instances where instance REGEXP 'large'"
    )
    length = len(results)
    assert length == 92

    results = db.execute(
        "SELECT DISTINCT instance from instances where NOT instance REGEXP 'large'"
    )
    assert len(results) == 100 - length

    results = db.execute(
        "SELECT DISTINCT cloud, instance from instances where cloud = 'aws'"
    )
    assert len(results) == 100
    results = db.execute(
        "SELECT DISTINCT cloud, cloudselect_id from instances where cloud = 'aws'"
    )
    assert len(results) == 100

    # Check result data keys
    for item in results:
        cloud, uid = item
        result = client.groups[cloud].generate_row(uid)
        for key in [
            "cloud",
            "name",
            "memory",
            "price",
            "cpus",
            "gpus",
            "region",
            "description",
        ]:
            assert key in result

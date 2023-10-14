#!/usr/bin/env python

# Copyright 2023 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)
#
# Save a cache of spot instance pricing.
# Note that you can get the spot placement score via this call
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/get_spot_placement_scores.html#EC2.Client.get_spot_placement_scores
# However it needs a certain instance type and number

import argparse
import os
import random
import pandas
import sys

from cloudselect.logger import setup_logger
from cloudselect.main import Client

here = os.path.dirname(os.path.abspath(__file__))


def get_parser():
    parser = argparse.ArgumentParser(
        description="Cloud Select Spot Instance Grouper",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--data",
        help="exported data.csv (to generate or use)",
        default="instances-aws.csv",
    )
    subparsers = parser.add_subparsers(
        help="cloudselect actions",
        title="actions",
        description="actions",
        dest="command",
    )
    gen = subparsers.add_parser(
        "gen",
        description="generate instance data frame",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    gen.add_argument(
        "--settings-file",
        dest="settings_file",
        help="custom path to settings file.",
    )
    gen.add_argument(
        "--cache-dir",
        dest="cache_dir",
        help="directory for data cache (defaults to $HERE/cache).",
        default=os.path.join(here, "cache"),
    )

    # On the fly updates to config params
    gen.add_argument(
        "-c",
        dest="config_params",
        help=""""customize a config value on the fly to ADD/SET/REMOVE for a command
cloud-select -c set:key:value <command> <args>
cloud-select -c add:registry:/tmp/registry <command> <args>
cloud-select -c rm:registry:/tmp/registry""",
        action="append",
    )

    # Select step
    select = subparsers.add_parser(
        "select",
        description="select from instance data frame",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    select.add_argument(
        "--arch",
        default="x86_64",
        help="architecture",
    )

    select.add_argument("--min-vcpu", help="minimum vCPU", type=int, default=32)
    select.add_argument("--max-vcpu", help="maximum vCPU", type=int, default=64)
    select.add_argument(
        "--max-threads-per-core",
        dest="threads_per_core",
        help="threads per core",
        type=int,
        default=2,
    )
    select.add_argument("--min-mem", help="minimum memory MB", type=int)
    select.add_argument("--max-mem", help="maximum memory MB", type=int)
    select.add_argument(
        "-n", "--number", help="number to select", type=int, dest="number"
    )
    return parser


def run():
    parser = get_parser()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, extra = parser.parse_known_args()

    # retrieve subparser (with help) from parser
    subparsers_actions = [
        action
        for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
    ]
    for subparsers_action in subparsers_actions:
        for choice, subparser in subparsers_action.choices.items():
            if choice == args.command:
                break

    # Be more verbose
    setup_logger(quiet=False, debug=True)

    if args.command == "gen":
        generate_data(args)
    elif args.command == "select":
        select_instances(
            args.data,
            args.arch,
            args.min_vcpu,
            args.max_vcpu,
            args.threads_per_core,
            args.min_mem,
            args.max_mem,
            args.number,
        )


def select_instances(
    datafile,
    arch,
    min_cpu,
    max_cpu,
    max_threads_per_core=2,
    min_mem=None,
    max_mem=None,
    number=None,
):
    """
    Given a csv of data, filter down / sort and show final set.
    """
    if not os.path.exists(datafile):
        sys.exit(f"Input data table {datafile} does not exist.")

    # Read in data frame
    df = pandas.read_csv(datafile, index_col=0)

    # Filter to arch and cpu (required)
    subset = df[df.arch == arch]
    subset = subset[subset.vcpu >= min_cpu]
    subset = subset[subset.vcpu <= max_cpu]
    subset = subset[subset.threads_per_core <= max_threads_per_core]

    # Optional memory
    if min_mem:
        subset = subset[min_mem <= subset.memory_mb]
    if max_mem:
        subset = subset[subset.memory_mb <= max_mem]

    # Sort by vcpu and then price
    sorted_df = subset.sort_values(["vcpu", "price"])
    instance_names = list(sorted_df.instance.values)

    # Honor a user threshold, if set
    if number and len(instance_names) > number:
        instance_names = instance_names[:number]
    for instance_name in instance_names:
        print(instance_name)
    return instance_names


def get_price_lookup(cloud):
    """
    Given a cloud, generate lookup of instance type by float price

    Note that I'm seeing instance types with USD 0.0 which doesn't make sense...
    """
    prices = cloud.prices()

    # Put together lookup by name
    lookup = {}
    for price in prices.data:
        if (
            "OnDemand" not in price["terms"]
            or "instanceType" not in price["product"]["attributes"]
        ):
            continue
        name = price["product"]["attributes"]["instanceType"]
        uid = list(price["terms"]["OnDemand"].keys())[0]
        lookup[name] = price["terms"]["OnDemand"][uid]
        dims = price["terms"]["OnDemand"][uid]["priceDimensions"]
        uid = list(dims.keys())[0]
        lookup[name] = float(dims[uid]["pricePerUnit"]["USD"])
    return lookup


def generate_data(args):
    """
    Generate and save data frame
    """
    # The client has a cache on it, cli.cache.
    # Set use_cache to False so we don't rely on it
    # This is currently just for aws
    cli = Client(
        settings_file=args.settings_file,
        cache_dir=args.cache_dir,
        use_cache=False,
        clouds=["aws"],
    )

    # Update config settings on the fly
    cli.settings.update_params(args.config_params)

    # Get new prices data for each cloud
    for cloud in cli.get_clouds():
        # Spot instances are aws for now
        if cloud.name != "aws":
            continue

        # Get prices for sorting!
        instances = cloud.instances()
        lookup = get_price_lookup(cloud)

        # Filter down to those that support spot (only a small number don't)
        instances = [x for x in instances.data if "spot" in x["SupportedUsageClasses"]]

        print(f"Found {len(instances)} instances on {cloud.name}")

        # There is more data here, this is what we want for now
        df = instances_to_table(instances, lookup)


def instances_to_table(instances, lookup):
    """
    Given listing of instances and price lookup, convert to table.
    """
    df = pandas.DataFrame(
        columns=[
            "instance",
            "bare_metal",
            "arch",
            "vcpu",
            "threads_per_core",
            "memory_mb",
            "price",
        ]
    )

    # Put into pandas data frame so we can sort / filter by:
    # architecture
    # memory
    # cpu
    # to start we will just care about arch and cpu
    idx = 0
    for i in instances:
        for arch in i["ProcessorInfo"]["SupportedArchitectures"]:
            if "window" in arch.lower():
                continue
            # What is the difference between DefaultCores and DefaultVCpu?
            cpus = i["VCpuInfo"]
            price = lookup.get(i["InstanceType"])
            df.loc[idx, :] = [
                i["InstanceType"],
                i["BareMetal"],
                arch,
                cpus["DefaultVCpus"],
                cpus["DefaultThreadsPerCore"],
                i["MemoryInfo"]["SizeInMiB"],
                price,
            ]
            idx += 1

    print(f"Saving {df.shape[0]} instances in table to {args.data}")
    df.to_csv(args.data)


if __name__ == "__main__":
    run()

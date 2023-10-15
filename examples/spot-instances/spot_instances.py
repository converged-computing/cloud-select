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
import sys

import pandas

from cloudselect.logger import setup_logger
from cloudselect.main import Client

here = os.path.dirname(os.path.abspath(__file__))

# Default architecture (also can do arm)
default_arch = "x86_64"


def get_parser():
    parser = argparse.ArgumentParser(
        description="Cloud Select Spot Instance Grouper",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--data",
        help="exported data.csv (to generate or use)",
        default=os.path.join(here, "instances-aws.csv"),
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
        "--no-cache", help="do not use cache", action="store_true", default=False
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
        default=default_arch,
        help="architecture",
    )

    select.add_argument(
        "--gpu", help="select instances with GPU", action="store_true", default=False
    )
    select.add_argument(
        "--randomize",
        help="randomize list (do not sort by price)",
        action="store_true",
        default=False,
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
    select.add_argument("--max-price", help="maximum price to set (USD/hour)", type=int)
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
            arch=args.arch,
            number=args.number,
            has_gpu=args.gpu,
            min_mem=args.min_mem,
            max_mem=args.max_mem,
            min_vcpu=args.min_vcpu,
            max_vcpu=args.max_vcpu,
            max_price=args.max_price,
            randomize=args.randomize,
            max_threads_per_core=args.threads_per_core,
        )


def select_instances(
    datafile,
    min_vcpu,
    max_vcpu=None,
    arch=default_arch,
    max_threads_per_core=2,
    min_mem=None,
    max_mem=None,
    number=None,
    has_gpu=False,
    max_price=None,
    randomize=False,
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
    subset = subset[subset.vcpu >= min_vcpu]
    subset = subset[subset.vcpu <= max_vcpu]
    subset = subset[subset.threads_per_core <= max_threads_per_core]

    # GPU
    subset = subset[subset.gpu == has_gpu]

    # Optional memory
    if min_mem:
        subset = subset[min_mem <= subset.memory_mb]
    if max_mem:
        subset = subset[subset.memory_mb <= max_mem]
    if max_price:
        subset = subset[subset.price <= max_price]

    # If not randomize, sort by vcpu and then price
    if not randomize:
        sorted_df = subset.sort_values(["vcpu", "price"])
    else:
        sorted_df = subset.sample(frac=1)

    instance_names = list(sorted_df.instance.values)

    # Honor a user threshold, if set
    if number and len(instance_names) > number:
        instance_names = instance_names[:number]

    sorted_df = sorted_df[sorted_df.instance.isin(instance_names)]
    print("Selected subset table:")
    print(sorted_df)

    print("\n😸️ Final selection of spot:")
    for instance_name in instance_names:
        print(instance_name)

    # Give mean cost and std
    print("\n🤓️ Mean (std) of price")
    mean = round(sorted_df.price.mean(), 2)
    std = round(sorted_df.price.std(), 2)
    print(f"${mean} (${std})")
    return sorted_df


def get_price_lookup(prices):
    """
    Given a cloud, generate lookup of instance type by float price

    Note that I'm seeing instance types with USD 0.0 which doesn't make sense...
    """
    # Put together lookup by name
    lookup = {}
    for price in prices.data:
        # Not an instance!
        if "instanceType" not in price["product"]["attributes"]:
            continue
        name = price["product"]["attributes"]["instanceType"]

        # No on demand price
        if "OnDemand" not in price["terms"]:
            continue
        uid = list(price["terms"]["OnDemand"].keys())[0]
        dims = price["terms"]["OnDemand"][uid]["priceDimensions"]
        uid = list(dims.keys())[0]
        usd = float(dims[uid]["pricePerUnit"]["USD"])

        # If USD is 0, this is usually an instance with addon like SQL (skip it)
        if usd == 0:
            continue
        lookup[name] = usd
    return lookup


def generate_data(args):
    """
    Generate and save data frame
    """
    # The client has a cache on it, cli.cache.
    # Set use_cache to False so we don't rely on it
    # This is currently just for aws
    cli = Client(use_cache=not args.no_cache, clouds=["aws"])

    # Update config settings on the fly
    cli.settings.update_params(args.config_params)

    # Get new prices data for each cloud
    for cloud in cli.get_clouds():
        # Spot instances are aws for now
        if cloud.name != "aws":
            continue

        # Get prices for sorting!
        instances = cli.instances()["aws"]
        prices = cli.prices()["aws"]
        lookup = get_price_lookup(prices)

        # Filter down to those that support spot (only a small number don't)
        instances = [x for x in instances.data if "spot" in x["SupportedUsageClasses"]]

        print(f"Found {len(instances)} instances on {cloud.name}")

        # There is more data here, this is what we want for now
        df = instances_to_table(instances, lookup)
        print(df)
        print(f"Saving {df.shape[0]} instances in table to {args.data}")
        df.to_csv(args.data)


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
            "gpu",
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
            gpu = "GpuInfo" in i
            price = lookup.get(i["InstanceType"])
            df.loc[idx, :] = [
                i["InstanceType"],
                i["BareMetal"],
                arch,
                cpus["DefaultVCpus"],
                cpus["DefaultThreadsPerCore"],
                i["MemoryInfo"]["SizeInMiB"],
                gpu,
                price,
            ]
            idx += 1
    return df


if __name__ == "__main__":
    run()

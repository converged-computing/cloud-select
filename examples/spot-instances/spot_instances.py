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
import statistics
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
    select.add_argument("--hypervisor", help="hypervisor")
    select.add_argument(
        "--gpu", help="select instances with GPU", action="store_true", default=False
    )
    select.add_argument(
        "--bare-metal",
        help="select instances with bare metal",
        action="store_true",
        default=False,
    )
    select.add_argument(
        "--randomize",
        help="randomize list (do not sort by price)",
        action="store_true",
        default=False,
    )
    select.add_argument("--min-cores", help="minimum physical cores", type=int)
    select.add_argument("--max-cores", help="maximum physical cores", type=int)
    select.add_argument("--min-vcpu", help="minimum vCPU", type=int)
    select.add_argument("--max-vcpu", help="maximum vCPU", type=int)
    select.add_argument(
        "--max-threads-per-core",
        dest="threads_per_core",
        help="threads per core",
        type=int,
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
            min_cores=args.min_cores,
            max_cores=args.max_cores,
            min_vcpu=args.min_vcpu,
            max_vcpu=args.max_vcpu,
            max_price=args.max_price,
            randomize=args.randomize,
            max_threads_per_core=args.threads_per_core,
            bare_metal=args.bare_metal,
            hypervisor=args.hypervisor,
        )


def select_instances(
    datafile,
    max_cores=None,
    min_cores=None,
    min_vcpu=None,
    max_vcpu=None,
    arch=default_arch,
    max_threads_per_core=None,
    min_mem=None,
    max_mem=None,
    number=None,
    has_gpu=False,
    max_price=None,
    max_spot_price=None,
    randomize=False,
    bare_metal=False,
    hypervisor=None,
):
    """
    Given a csv of data, filter down / sort and show final set.

    Arch defaults to x86_64 and gpu none
    """
    if not os.path.exists(datafile):
        sys.exit(f"Input data table {datafile} does not exist.")

    # Read in data frame
    df = pandas.read_csv(datafile, index_col=0)

    # Filter to arch and cores
    subset = df[df.arch == arch]

    if min_cores:
        subset = subset[subset.cores >= min_cores]
    if max_cores:
        subset = subset[subset.cores <= max_cores]

    # GPU
    subset = subset[subset.gpu == has_gpu]

    # More detail about cpu / threads
    if min_vcpu:
        subset = subset[subset.vcpu >= min_vcpu]
    if max_vcpu:
        subset = subset[subset.vcpu <= max_vcpu]
    if max_threads_per_core:
        subset = subset[subset.threads_per_core <= max_threads_per_core]

    # Optional memory
    if min_mem:
        subset = subset[min_mem <= subset.memory_mb]
    if max_mem:
        subset = subset[subset.memory_mb <= max_mem]
    if max_price:
        subset = subset[subset.price <= max_price]
    if max_spot_price:
        subset = subset[subset.spot_price <= max_spot_price]
    if hypervisor:
        subset = subset[subset.hypervisor == hypervisor]

    if bare_metal:
        subset = subset[subset.bare_metal is True]
    else:
        subset = subset[subset.bare_metal is False]

    # If not randomize, sort by vcpu and then price
    if not randomize:
        sorted_df = subset.sort_values(["vcpu", "spot_price"])
    else:
        sorted_df = subset.sample(frac=1)

    instance_names = list(sorted_df.instance.values)

    # Show the user the maximum price in the current set
    max_spot = sorted_df.spot_price.max()
    min_spot = sorted_df.spot_price.min()
    print(f"\n☝️  Max spot price: {max_spot}")
    print(f"👇️ Min spot price: {min_spot}")

    # Honor a user threshold, if set
    if number and len(instance_names) > number:
        instance_names = instance_names[:number]

    sorted_df = sorted_df[sorted_df.instance.isin(instance_names)]
    print("\n😸️ Filtered selection of spot:")
    print(sorted_df)

    # Give mean cost and std
    print("\n🤓️ Mean (std) of spot price")
    mean = round(sorted_df.spot_price.mean(), 2)
    std = round(sorted_df.spot_price.std(), 2)
    print(f"${mean} (${std})\n")
    return sorted_df


def get_price_lookup(prices, spot_prices):
    """
    Given a cloud, generate lookup of instance type by float price

    Note that I'm seeing instance types with USD 0.0 which doesn't make sense...
    """
    # Put together lookup by name. We will take mean across availability zones
    lookup = {}
    means = {}
    for instance_type, zones in spot_prices.items():
        sps = [float(x["SpotPrice"]) for _, x in zones.items()]
        means[instance_type] = statistics.mean(sps)

    for price in prices.data:
        if "instanceType" not in price["product"]["attributes"]:
            continue
        if price["product"]["attributes"]["operatingSystem"] != "Linux":
            continue
        # WARNING: this is hard coded here to match the prices data default
        if price["product"]["attributes"]["regionCode"] != "us-east-1":
            continue
        name = price["product"]["attributes"]["instanceType"]

        # Skip instance that don't have spot
        if name not in means:
            continue

        # We need OnDemand too
        if "OnDemand" not in price["terms"]:
            continue

        # This seems to be the best way to find the on demand linux for the instance type
        # There are a LOT
        usd = None
        for _, meta in price["terms"].items():
            for _, pds in meta.items():
                for _, pd in pds["priceDimensions"].items():
                    if pd["unit"] != "Hrs":
                        continue
                    if f"On Demand Linux {name}" in pd["description"]:
                        usd = pd["pricePerUnit"]["USD"]

        # This isn't the right instance type
        if not usd:
            continue
        if usd and name in lookup:
            print(f"Warning: found previous price for {name}: {lookup[name]}")
        lookup[name] = {"price": float(usd), "spot_price": means[name]}
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
        instances = cli.instances()["aws"]
        prices = cli.prices()["aws"]

        # Get spot prices
        spot_prices = cloud.spot_prices(instances)
        lookup = get_price_lookup(prices, spot_prices)

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
            "cores",  # this is physical cores
            "threads_per_core",
            "memory_mb",
            "hypervisor",
            "gpu",
            "spot_price",
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
            price = lookup.get(i["InstanceType"])["price"]
            spot_price = lookup.get(i["InstanceType"])["spot_price"]
            hypervisor = i.get("Hypervisor")

            # If 1 thread not possible, don't include
            if cpus["DefaultThreadsPerCore"] != 1:
                if (
                    "ValidThreadsPerCore" not in cpus
                    or 1 not in cpus["ValidThreadsPerCore"]
                ):
                    print(
                        f'Skipping {i["InstanceType"]}, does not support 1 thread per core.'
                    )
                    continue

            df.loc[idx, :] = [
                i["InstanceType"],
                i["BareMetal"],
                arch,
                cpus["DefaultVCpus"],
                cpus["DefaultCores"],
                cpus["DefaultThreadsPerCore"],
                i["MemoryInfo"]["SizeInMiB"],
                hypervisor,
                gpu,
                spot_price,
                price,
            ]
            idx += 1
    return df


if __name__ == "__main__":
    run()

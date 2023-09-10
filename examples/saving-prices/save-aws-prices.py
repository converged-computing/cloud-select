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
import sys

from cloudselect.main import Client

here = os.path.dirname(os.path.abspath(__file__))


def get_parser():
    parser = argparse.ArgumentParser(
        description="Cloud Select Price Exporter",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--verbose",
        dest="verbose",
        help="print additional solver output (atoms).",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--settings-file",
        dest="settings_file",
        help="custom path to settings file.",
    )

    # Save a local cache right here
    parser.add_argument(
        "--cache-dir",
        dest="cache_dir",
        help="directory for data cache (defaults to ~/.cloud-select/cache).",
        default=os.path.join(here, "cache"),
    )

    # On the fly updates to config params
    parser.add_argument(
        "-c",
        dest="config_params",
        help=""""customize a config value on the fly to ADD/SET/REMOVE for a command
cloud-select -c set:key:value <command> <args>
cloud-select -c add:registry:/tmp/registry <command> <args>
cloud-select -c rm:registry:/tmp/registry""",
        action="append",
    )

    parser.add_argument(
        "--push-to",
        dest="push_to",
        action="append",
        help="push cache data to GitHub packages URI (can be used for more than one URI)",
    )
    parser.add_argument(
        "--target-units",
        dest="target_units",
        help="Number of target units for score (defaults to 10)",
        default=10,
        type=int,
    )
    parser.add_argument(
        "--update",
        help="force an update of cache data",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--clear",
        help="clear the cache",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--force",
        help="force clear of the cache (with no prompt)",
        default=False,
        action="store_true",
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
        # Alert user if no permissions.
        # Note that this often requires asking for special permissions from your cloud manager
        if not cloud.has_pricing_auth:
            print(
                f"WARNING: You do not have permission to use the pricing API for {cloud}."
            )
            continue

        # This gets ALL pricing data, can take a while! (25-30 minutes)
        # There are upwards of 100K records
        prices = cloud.prices()

        # Separate into category based on instance types. Note we are throwing away a lot here - here
        # are all the product types
        # 'CPU Credits',
        # 'Compute Instance',
        # 'Compute Instance (bare metal)',
        # 'Data Transfer',
        # 'Dedicated Host',
        # 'EBS direct API Requests',
        # 'Elastic Graphics',
        # 'Fast Snapshot Restore',
        # 'Fee',
        # 'IP Address',
        # 'Load Balancer',
        # 'Load Balancer-Application',
        # 'Load Balancer-Network',
        # 'NAT Gateway',
        # 'Provisioned Throughput',
        # 'Storage',
        # 'Storage Snapshot',
        # 'System Operation'}

        instances = {}
        total = len(prices.data)
        instance_names = set()
        for i, item in enumerate(prices.data):
            print(f"Organizing {i} of {total}", end="\r")
            family = item["product"]["productFamily"]
            if "Compute Instance" not in family:
                continue
            instance_type = item["product"]["attributes"]["instanceType"]
            instance_names.add(instance_type)
            region = item["product"]["attributes"]["regionCode"]
            key = f"{region}_{instance_type}"
            if key not in instances:
                instances[key] = []
            instances[key].append(item)

        # Now save each one, based on the key
        for key, data in instances.items():
            cache_name = f"prices-{key}"
            print(f"Saving cache data for {cache_name}")
            cli.cache.set(cloud.name, data, cache_name)

        # These are invalid types to get scores for
        invalid_types = [
            "p4de.24xlarge",
            "cr1.8xlarge",
            "hs1.8xlarge",
            "cc2.8xlarge",
            "i2.large",
        ]

        instance_names = [x for x in instance_names if x not in invalid_types]

        # Try to get a different sample each time
        instance_names = list(instance_names)
        random.shuffle(instance_names)

        # Get score for each type (based on prefix)
        by_prefix = {}
        for instance_name in instance_names:
            prefix = instance_name.split(".")[0]
            if prefix not in by_prefix:
                by_prefix[prefix] = []
            by_prefix[prefix].append(instance_name)

        # Group scores by prefixes
        scores = {}
        for prefix, instance_list in by_prefix.items():
            # It looks like we can do 50 calls out of 112 prefixes
            try:
                print(f"Getting spot score for instance type {prefix}")
                # Get scores for each one, an arbitrary workload
                score = cloud.ec2_client.get_spot_placement_scores(
                    InstanceTypes=instance_list,
                    RegionNames=cloud.regions,
                    TargetCapacity=args.target_units,
                    TargetCapacityUnitType="units",
                    # SingleAvailabilityZone=True|False,
                    # Instead of instance types we can do:
                    # InstanceRequirementsWithMetadata
                    # DryRun=True|False,
                    # MaxResults=123,
                )
                scores[prefix] = {
                    "instance": instance_list,
                    "score": score["SpotPlacementScores"],
                }
            except Exception as e:
                print(f"Likely hit API limit, stopping for today: {e}")

        # Save scores
        cli.cache.set(cloud.name, scores, f"scores-{cloud.regions[0]}")

        # Push the cache!
        if not args.push_to:
            print("No --push-to specified, done!")
            sys.exit()

        # Push to specified URIs
        for uri in args.push_to:
            print(f"Pushing to {uri}")
            cli.cache.push(uri, require_all=False)


if __name__ == "__main__":
    run()

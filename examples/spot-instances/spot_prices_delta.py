#!/usr/bin/env python

# Copyright 2023 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)
#
# Generate distributions of deltas (between price reports)
# for each spot instance type.

import argparse
import os
from datetime import datetime, timedelta

import cloudselect.utils as utils
from cloudselect.logger import setup_logger
from cloudselect.main import Client

here = os.path.dirname(os.path.abspath(__file__))


def get_parser():
    parser = argparse.ArgumentParser(
        description="Cloud Select Spot Instance Deltas",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--data",
        help="exported data.csv (to generate or use)",
        default=os.path.join(here, "spot-price-deltas.csv"),
    )
    return parser


def run():
    parser = get_parser()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, extra = parser.parse_known_args()

    # Be more verbose
    setup_logger(quiet=False, debug=True)
    generate_data(args)


def generate_data(args):
    """
    Generate and save data of spot price deltas over time
    """
    # The client has a cache on it, cli.cache.
    # Set use_cache to False so we don't rely on it
    # This is currently just for aws
    cli = Client(use_cache=True, clouds=["aws"])

    # Get new prices data for each cloud
    for cloud in cli.get_clouds():
        # Spot instances are aws for now
        if cloud.name != "aws":
            continue

        # Get spot prices since last week
        instances = cli.instances()["aws"]
        last_week = datetime.now() - timedelta(days=7)
        spot_prices = cloud.spot_prices(instances, since=last_week, latest=False)

        # Organize by instance type, avail. zone
        data = {}
        for price in spot_prices:
            instance = price["InstanceType"]
            azone = price["AvailabilityZone"]
            if instance not in data:
                data[instance] = {}
            if azone not in data[instance]:
                data[instance][azone] = []
            data[instance][azone].append(price["Timestamp"])

        # Sort each one
        for instance, zones in data.items():
            for zone, dates in zones.items():
                # This sorts least to greatest (err most recent)
                dates.sort()

        # Now calculate a delta between each (could have used same loop, it's OK)
        deltas = {}
        for instance, zones in data.items():
            for zone, times in zones.items():
                if instance not in deltas:
                    deltas[instance] = {}
                if zone not in deltas[instance]:
                    deltas[instance][zone] = []
                for i in range(0, len(times) - 1):
                    current = i
                    next = i + 1
                    diff = times[next] - times[current]
                    deltas[instance][zone].append(
                        {
                            "seconds": diff.seconds,
                            "minutes": diff.seconds / 60,
                            "hours": diff.seconds / 60 / 60,
                        }
                    )

        # Note that these are the same times, but just different units
        # seconds / minutes / hours
        utils.write_json(deltas, "aws-spot-price-deltas.json")


if __name__ == "__main__":
    run()

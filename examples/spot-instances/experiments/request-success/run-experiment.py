#!/usr/bin/env python3

import argparse
import copy
import json
import os
import random
import sys

from kubescaler.scaler.aws import EKSCluster

# import the script we have two levels up
here = os.path.abspath(os.path.dirname(__file__))
import_dir = os.path.dirname(os.path.dirname(here))

# This data file must exist, it has a full price table
data_file = os.path.join(import_dir, "instances-aws.csv")
sys.path.insert(0, import_dir)

import spot_instances as spot_cli  # noqa

# Exit early if we haven't generated the data
if not os.path.exists(data_file):
    sys.exit(f"Cannot find {data_file}! Run spot_instances.py gen first.")

# These are the criteria we are going to use for the experiment.
# This could easily be moved into a data file to read, I'm just lazy right now
# see the readme for details, and feel free to add here to customize
experiment_plans = [
    {"vcpu": 4, "max-instance-types": 10},
    #    {"vcpu": 8, "max-instance-types": 10},
    #    {"vcpu": 16, "max-instance-types": 10},
    #    {"vcpu": 32, "max-instance-types": 10},
]


def get_parser():
    parser = argparse.ArgumentParser(
        description="Spot Instance Experiment Running",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--max-instance-types",
        help="maximum instance types to select from (if not set in experiment plan)",
        type=int,
        default=10,
    )
    parser.add_argument(
        "--cluster-name",
        help="cluster name to use (defaults to spot-instance-testing-cluster",
        default="spot-instance-testing-cluster",
    )
    parser.add_argument(
        "--min-spot-request",
        help="smallest number of instances to test requesting for spot",
        type=int,
        default=2,
    )
    parser.add_argument(
        "--max-spot-request",
        help="largest number of instances to test requesting for spot",
        type=int,
        default=4,
    )
    parser.add_argument(
        "--outfile",
        help="output json file to save results to (as we go) defaults to cluster name",
    )
    parser.add_argument(
        "--plan",
        help="plan (json) file to parse",
    )
    parser.add_argument(
        "--nodes",
        help="number of nodes to request (defaults to 4 for testing)",
        type=int,
        default=4,
    )
    return parser


class Experiment:
    """
    An Experiment holds a set of parameters and handles load, save, etc.
    """

    def __init__(self, plan, max_instance_types=10):
        self.load(plan)
        self._max_instance_types = max_instance_types

    def load(self, plan):
        """
        Load (or reload) an experiment into the class.
        """
        self.plan = plan
        # The uid just smashes all the fields together
        self.id = generate_uid(plan)

        # Note we are setting min == max to get a consistent value. Arch defaults to x86_64 and gpu none
        self.df = spot_cli.select_instances(
            data_file,
            min_vcpu=self.plan["vcpu"],
            max_vcpu=self.plan["vcpu"],
            number=self.max_instance_types,
        )

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.id}.Experiment"

    @property
    def max_instance_types(self):
        return self.plan.get("max-instance-types") or self._max_instance_types

    def export(self):
        """
        Export experiment metadata
        """
        return {
            "runs": [],
            "plan": self.plan,
            "instances": self.df.to_csv(),
            "max_instance_types": self.max_instance_types,
        }

    @property
    def count(self):
        """
        Show the number of instances selected.
        """
        return self.df.shape[0]

    def select_machine_types(self, count):
        """
        Generate an experiment by randomly selecting from the instances

        We always choose randomly here.
        """
        listing = list(self.df.instance.values)
        random.shuffle(listing)
        selected = listing[:count]
        subset = self.df[self.df.instance.isin(selected)]
        show_selected(subset)
        return subset


def show_selected(df):
    """
    Given a selected dataframe, show it (and the price)
    """
    print("\n✅️ Selected instances")
    print(df)
    print("\n✅️ Mean (std) of price")
    mean = round(df.price.mean(), 2)
    std = round(df.price.std(), 2)
    print(f"${mean} (${std})")


def read_json(filename):
    with open(filename, "r") as fd:
        content = json.loads(fd.read())
    return content


def confirm_action(question):
    """
    Ask for confirmation of an action
    """
    response = input(question + " (yes/no)? ")
    while len(response) < 1 or response[0].lower().strip() not in "ynyesno":
        response = input("Please answer yes or no: ")
    if response[0].lower().strip() in "no":
        return False
    return True


def plan_experiments(args):
    """
    Given experiment "plans" create a matrix of actual experiments (and instance types) to run
    """
    experiments = {}
    # Were we given a plan in json?
    if args.plan and os.path.exists(args.plan):
        print(f"Loading plans from {args.plan}")
        experiment_plans = read_json(args.plan)

    for plan in experiment_plans:
        print(f"🧪️ Planning experiments for {plan}")
        exp = Experiment(plan, max_instance_types=args.max_instance_types)

        # Save us from ourselves.
        if exp.id in experiments:
            print(
                f"📛️ WARNING: identifier {exp.id} is already present, meaning you have equivalent parameters in two experiments."
            )
            continue

        # No instances available
        if exp.count == 0:
            print(
                f"📛️ WARNING: identifier {exp.id} selected no instances, and cannot be run."
            )
            continue

        experiments[exp.id] = exp
    return experiments


def generate_uid(params):
    """
    Generate a unique id based on params.
    """
    uid = ""
    for k, v in params.items():
        uid += k.lower() + "-" + str(v).lower()
    return uid


def write_json(obj, filename):
    """
    write json to output file
    """
    with open(filename, "w") as fd:
        fd.write(json.dumps(obj, indent=4))


def main():
    """
    Demonstrate creating and deleting a cluster. If the cluster exists,
    we should be able to retrieve it and not create a second one.
    """
    parser = get_parser()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, _ = parser.parse_known_args()

    # Result file
    if not args.outfile:
        args.outfile = f"{args.cluster_name}-results.json"

    # Min cannot be >= max
    if args.min_spot_request >= args.max_spot_request:
        sys.exit("Oops, the minimum spot request needs to be less than the max!")

    # plan experiments!
    experiments = plan_experiments(args)
    count = len(range(args.min_spot_request, args.max_spot_request))
    print("🧪️ Experiments:")
    for exp in experiments:
        print(f"   {exp}")

    print("🪴️ Planning to run:")
    print(f"   Cluster name        : {args.cluster_name}")
    print(f"   Output File         : {args.outfile}")
    print(f"   Experiments         : {len(experiments)}")
    print(f"   Nodes requested     : {args.nodes}")
    print(f"   Max Instance Types  : {args.max_instance_types}")
    print(
        f"   Range Spot Requests : {count} ({args.min_spot_request} to {args.max_spot_request})"
    )
    if not confirm_action("Would you like to continue?"):
        sys.exit("Cancelled!")

    # Use kubescaler ekscluster to create the cluster
    # We will request / delete nodegroups from it
    cli = EKSCluster(
        name=args.cluster_name,
        eks_nodegroup=True,
        capacity_type="SPOT",
        node_count=args.nodes,
        min_nodes=args.nodes,
        max_nodes=args.nodes,
    )

    # Note we are NOT creating the node group here - just the cluster, so machine types aren't relevant
    # We will add machine types as node groups (to create and delete from the cluster) later
    cli.create_cluster(create_nodes=False)

    # Save results as we go!
    original_times = cli.times
    results = {
        "experiments": {},
        "times": original_times,
        "nodes": args.nodes,
        "cluster_name": args.cluster_name,
    }

    for name, exp in experiments.items():
        print(f"== Experiment {exp.id} has {exp.count} instances selected.")

        # Add specific experiment to results
        results["experiments"][name] = exp.export()

        # We will generate from args.min (2) up to the count
        for count in range(args.min_spot_request, args.max_spot_request):
            # Reset times between experiments
            cli.times = {}

            # Here we select our random machine types from the set (this shows/prints it too)
            # This returns a subset of the data frame. The entire experiment df is saved with experiment
            subset = exp.select_machine_types(count)
            machine_types = list(subset.instance.values)

            # Now create the node groups!
            cli.create_cluster_nodes(machine_types)

            # And now... delete it! We don't need it, lol
            cli.delete_nodegroup(cli.node_group_name)

            # Add cluster times to the new times
            times = copy.deepcopy(original_times)
            times.update(cli.times)

            # Save metadata as we go - the times include for the cluster too
            # We might as well make mean price easy to see too
            new_result = {
                "machine_types": machine_types,
                "count": count,
                "times": times,
                "mean_price": subset.price.mean(),
                "std_price": subset.price.std(),
            }
            print(json.dumps(new_result))
            results["experiments"][name]["runs"].append(new_result)
            write_json(results, args.outfile)

    # When we are done, delete the cluster
    cli.times = {}
    cli.delete_cluster()

    # Update original times with deletion times
    times = copy.deepcopy(original_times)
    times.update(cli.times)
    results["times"] = times
    write_json(results, args.outfile)


if __name__ == "__main__":
    main()

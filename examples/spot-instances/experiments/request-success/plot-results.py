#!/usr/bin/env python3

# Analyze results for pod events and make summary plots.
import argparse
import collections
import io
import json
import os
import re
import sys

import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from matplotlib.ticker import FormatStrFormatter

plt.style.use("bmh")

# Save data here
here = os.path.dirname(os.path.abspath(__file__))

# Assume input directory is data
data = os.path.join(here, "data")
results = os.path.join(here, "img")


def recursive_find(base, pattern=None):
    """
    Find filenames that match a particular pattern, and yield them.
    """
    # We can identify modules by finding module.lua
    for root, folders, files in os.walk(base):
        for file in files:
            fullpath = os.path.abspath(os.path.join(root, file))

            if pattern and not re.search(pattern, fullpath):
                continue
            yield fullpath


def write_json(obj, path):
    """
    write json to file
    """
    with open(path, "w") as fd:
        fd.write(json.dumps(obj, indent=4))


def get_parser():
    parser = argparse.ArgumentParser(
        description="Spot Instance Plotter",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--outdir", help="Path for the parsed results", default=results)
    parser.add_argument("data", help="Data json file with experiment results to plot")
    return parser


def read_json(filename):
    with open(filename, "r") as file:
        content = json.loads(file.read())
    return content


def read_data(data):
    """
    parse results into pandas data frame
    """
    # TODO we only have one set of times here (for cluster creation / deletion) but eventually
    # this will be interesting to plot when we have > 1.

    for name, exp in data["experiments"].items():
        # How to read original instance df
        pandas.read_csv(io.StringIO(exp["instances"]), sep=",", index_col=0)

        # Assemble into data frame
        df = pandas.DataFrame(
            columns=[
                "experiment",
                "count",
                "mean_hourly_price",
                "std_hourly_price",
                "nodes_creation_seconds",
                "nodes_deletion_seconds",
                "wait_nodes_seconds",
            ]
        )

        # Oversight forgot to save nodes first time around...
        nodes = exp.get("nodes", 8)
        idx = 0
        for run in exp["runs"]:
            create_seconds = run["times"][f"create_cluster_nodes-size-{nodes}"]
            delete_seconds = run["times"][f"delete_nodegroup-size-{nodes}"]
            wait_seconds = run["times"][f"wait_for_nodes-size-{nodes}"]
            df.loc[idx, :] = [
                name,
                run["count"],
                run["mean_price"],
                run["std_price"],
                create_seconds,
                delete_seconds,
                wait_seconds,
            ]
            idx += 1
    return df


def main():
    parser = get_parser()

    # If an error occurs while parsing the arguments, the interpreter will exit with value 2
    args, _ = parser.parse_known_args()

    if not args.data or not os.path.exists(args.data):
        sys.exit("Please provide the input json file as the only argument")
    if not os.path.isfile(args.data):
        sys.exit("Please provide a single json file.")

    # Generate a pandas data frame of parsed results
    data = read_json(args.data)
    print(f"🤓️ Reading data for {len(data['experiments'])} experiments...")
    df = read_data(data)

    # Prepare output directory with plots
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    # Save data to csv alongside original json file
    outfile = os.path.basename(args.data).split(".")[0] + "csv"
    df.to_csv(os.path.join(args.outdir, outfile))

    # plot the results!
    for name in df.experiment.unique():
        print(f"Plotting results for {name}")
        subset = df[df.experiment == name]
        plot_data(subset, args.outdir, name)


def plot_data(df, outdir, name):
    """
    Plot results into data frame
    """
    # Plot each!
    colors = sns.color_palette("hls", 16)
    hexcolors = colors.as_hex()
    types = list(df["count"].unique())
    types.sort()

    # ALWAYS double check this ordering, this
    # is almost always wrong and the colors are messed up
    palette = collections.OrderedDict()
    for t in types:
        palette[t] = hexcolors.pop(0)

    make_plot(
        df,
        x="count",
        y="nodes_creation_seconds",
        hue="count",
        palette=palette,
        title="AWS Spot Instance NodeGroup Creation Times as a Function of Instance Types Count",
        xlabel="Instance Types Allowed (count)",
        ylabel="Seconds",
        saveto=os.path.join(outdir, f"{name}-creation-times.png"),
    )

    make_plot(
        df,
        x="count",
        y="mean_hourly_price",
        hue="count",
        palette=palette,
        title="AWS Spot Instance NodeGroup Prices as a Function of Instance Types Count",
        xlabel="Instance Types Allowed (count)",
        ylabel="Seconds",
        saveto=os.path.join(outdir, f"{name}-prices.png"),
    )


def make_plot(df, x, y, hue, palette, title, xlabel, ylabel, saveto):
    """
    Make a standard plot - scatter for now with one point!
    """
    # Fix warning at some point :)
    # https://stackoverflow.com/questions/63723514/userwarning-fixedformatter-should-only-be-used-together-with-fixedlocator
    plt.figure(figsize=(12, 8))
    ax = sns.scatterplot(data=df, x=x, y=y, hue=hue, palette=palette)
    plt.title(title)
    ax.set_xlabel(xlabel, fontsize=16)
    ax.set_ylabel(ylabel, fontsize=16)
    ax.set_xticklabels(ax.get_xmajorticklabels(), fontsize=14)
    ax.set_yticklabels(ax.get_yticks(), fontsize=14)
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.2f"))
    plt.savefig(saveto)
    plt.clf()
    plt.close()


if __name__ == "__main__":
    main()

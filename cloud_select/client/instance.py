# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

import json
import os
import sys

import cloud_select.main.table as table
import cloud_select.utils as utils
from cloud_select.main import Client


def main(args, parser, extra, subparser):

    utils.ensure_no_extra(extra)

    cli = Client(
        quiet=args.quiet,
        settings_file=args.settings_file,
        cache_dir=args.cache_dir,
        cache_expire=args.cache_expire,
        clouds=args.clouds,
    )

    # Update config settings on the fly
    cli.settings.update_params(args.config_params)

    # Are we writing ASP to an output file?
    asp_out = None
    out = args.out
    if args.asp_out is not None:
        asp_out = open(args.asp_out, "w")

    # Or default to being more quiet
    elif not args.verbose:
        asp_out = open(os.devnull, "w")
    elif args.verbose:
        asp_out = sys.stdout

    # Clean up extra attributes
    for attr in "asp_out", "out":
        delattr(args, attr)

    # And select the instance (this output is for the ASP)
    instances = cli.instance_select(**args.__dict__, out=asp_out)
    if asp_out is not None:
        asp_out.close()

    # Print instances to a table
    if args.json:
        print(json.dumps(instances, indent=4))
    elif out:
        utils.write_json(out, instances)
    else:
        t = table.Table(instances)
        t.table(title="Cloud Instances Selected")

# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

import json

import cloudselect.main.table as table
import cloudselect.utils as utils
from cloudselect.logger import logger
from cloudselect.main import Client


def main(args, parser, extra, subparser):
    utils.ensure_no_extra(extra)

    cli = Client(
        quiet=args.quiet,
        settings_file=args.settings_file,
        cache_dir=args.cache_dir,
        cache_expire=args.cache_expire,
        use_cache=not args.no_cache,
        clouds=args.clouds,
    )

    # Update config settings on the fly
    cli.settings.update_params(args.config_params)

    # If max results is 0, set to None (no limit)
    if args.max_results == 0:
        args.max_results = None

    # Are we writing ASP to an output file?
    out = args.out
    delattr(args, "out")

    # And select the instance (this output is for the ASP)
    try:
        instances = cli.instance_select(**args.__dict__)
    except Exception as e:
        logger.exit(str(e))

    # Print instances to a table
    if args.json:
        print(json.dumps(instances, indent=4))
    elif out:
        utils.write_json(out, instances)
    else:
        t = table.Table(instances)
        t.table(
            title="Cloud Instances Selected",
            sort_by=args.sort_by,
            limit=args.max_results,
            ascending=args.ascending,
        )

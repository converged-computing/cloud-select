# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

import json

import cloud_select.utils
from cloud_select.main import Client


def main(args, parser, extra, subparser):

    cloud_select.utils.ensure_no_extra(extra)

    cli = Client(
        quiet=args.quiet,
        settings_file=args.settings_file,
        cache_dir=args.cache_dir,
        cache_expire=args.cache_expire,
    )

    # Update config settings on the fly
    cli.settings.update_params(args.config_params)

    # Are we writing to an output file?
    out = None
    if args.out is not None and not args.quiet:
        out = open(args.out, "w")
    delattr(args, "out")

    # And select the instance
    instances = cli.instance_select(**args.__dict__, out=out)
    print(json.dumps(instances, indent=4))
    if out:
        out.close()

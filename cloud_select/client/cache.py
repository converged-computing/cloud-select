# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

import cloud_select.utils as utils
from cloud_select.main import Client


def main(args, parser, extra, subparser):

    utils.ensure_no_extra(extra)

    cli = Client(
        quiet=args.quiet,
        settings_file=args.settings_file,
        cache_dir=args.cache_dir,
        clouds=args.clouds,
    )

    # Update config settings on the fly
    cli.settings.update_params(args.config_params)

    # Do we want to clear the cache?
    if args.clear:
        cli.cache.clear(force=args.force)

    # Update prices and instances for all clouds we can
    if args.update:
        cli.update_all()

    # Push to an ORAS registry (e.g., GitHub packages)
    if args.push:
        cli.cache.push(args.push)

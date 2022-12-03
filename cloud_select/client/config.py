# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

import sys

import cloud_select.defaults as defaults
import cloud_select.utils
from cloud_select.logger import logger


def main(args, parser, extra, subparser):

    from cloud_select.main import get_client

    cloud_select.utils.ensure_no_extra(extra)

    # If nothing provided, show help
    if not args.params:
        print(subparser.format_help())
        sys.exit(0)

    # The first "param" is either set of get
    command = args.params.pop(0)

    # If the user wants the central config file
    if args.central:
        args.settings_file = defaults.default_settings_file

    validate = True if not command == "edit" else False
    cli = get_client(
        quiet=args.quiet, settings_file=args.settings_file, validate=validate
    )

    # For each new setting, update and save!
    if command == "inituser":
        return cli.settings.inituser()
    if command == "edit":
        return cli.settings.edit()

    if command in ["set", "add", "remove"]:
        cli.settings.update_param(command, args.params)

        # Save settings
        cli.settings.save()

    # For each get request, print the param pair
    elif command == "get":
        for key in args.params:
            value = cli.settings.get(key)
            value = "is unset" if value is None else value
            logger.info("%s %s" % (key.ljust(30), value))

    else:
        logger.error("%s is not a recognized command." % command)

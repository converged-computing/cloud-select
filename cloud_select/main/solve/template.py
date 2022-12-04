# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

# base template of logic program

import os

import cloud_select.utils as utils
from cloud_select.logger import logger


def load_template(name):
    """
    Load a named template from the logic program folder.
    """
    here = os.path.abspath(os.path.dirname(__file__))
    template_file = os.path.join(here, "lp", name)
    if os.path.exists(template_file):
        return utils.read_file(template_file)


def write_instance_select_program(props, tmpfile=None):
    """
    Write the logic program to file, given chosen attributes.
    """
    if not tmpfile:
        tmpfile = utils.get_tmpfile()

    # Add back if/when extra rules
    template = load_template("instance-select.lp")
    if not template:
        logger.exit(
            "Cannot load instance-select.lp, possible problem with installation."
        )

    rule = "select(Cloud, Instance)."
    if props:
        rule = "select(Cloud, Instance) :-"
        for i, key in enumerate(props):
            value = props[key]
            if isinstance(value, bool):
                value = str(value).lower()
            if isinstance(value, str):
                value = f'"{value}"'
            rule += f'\n    has_attr(Cloud, Instance, "{key}", {value})'
            # Last one is a period.
            if i == len(props) - 1:
                rule += "."
            else:
                rule += ","

    template += "\n\n" + rule + "\n\n" + "#show select/2."
    utils.write_file(tmpfile, template)
    print(template)
    return tmpfile

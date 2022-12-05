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


def write_instance_select_program(props, tmpfile=None, out=None):
    """
    Write the instance select program, optionally writing to an output
    file the user has requested.
    """
    if not tmpfile:
        tmpfile = utils.get_tmpfile()

    # Add back if/when extra rules
    template = load_template("instance-select.lp")
    if not template:
        logger.exit(
            "Cannot load instance-select.lp, possible problem with installation."
        )
    select_program = generate_instance_select_program(props)
    template += "\n\n" + select_program + "\n\n" + "#show select/2."
    utils.write_file(tmpfile, template)
    if out is not None:
        out.write(template)
    return tmpfile


def generate_instance_select_program(props):
    """
    Generate the partial logic program to add to the template with chosen attributes.
    """
    # First we parse the range rules - need a most / least / in range
    template = generate_instance_range_rules(props)

    rule = "select(Cloud, Instance)."
    if props:
        rule = "select(Cloud, Instance) :-"
        for i, key in enumerate(props):
            value = props[key]
            value = parse_value(value)
            # Case 1: we have a range with lookup min/max
            if key.startswith("range:"):
                rule += parse_range(key, value)
            # Case 2: looking for an exact match
            else:
                rule += f'\n    has_attr(Cloud, Instance, "{key}", {value})'
            # Commas are AND and last one is a period to end statement.
            if i == len(props) - 1:
                rule += "."
            else:
                rule += ","

    template = template + "\n\n" + rule
    return template


def generate_instance_range_rules(props):
    """
    Provide the solver with facts about mins/max and ranges.
    """
    template = ""
    for key, value in props.items():
        if "range:" not in key:
            continue

        key = key.replace("range:", "", 1)
        min_value = value["min"]
        max_value = value["max"]

        if min_value is not None and max_value is not None:
            template += f'\nneed_in_range("{key}", {min_value}, {max_value}).\n'

        elif min_value is not None:
            template += f'\nneed_at_least("{key}", {min_value}).\n'

        else:
            template += f'\nneed_at_most("{key}", {max_value}).\n'
    return template


def parse_range(key, value):
    """
    Given a stated range, e.g.,:

    range_gpus: {'min': 2, 'max': None}

    Return either a min/max rule, or just a min,or just a max.
    """
    # If we get to a range without min/max this is an error (and shouldn't happen)
    key = key.replace("range:", "", 1)
    min_value = value["min"]
    max_value = value["max"]

    # Custom variables for the body for each of min and max
    actual = "Value" + key.capitalize()
    template = ""

    if min_value is not None and max_value is not None:
        template += f"\n    need_in_range(Attribute, Min{actual}, Max{actual}),"
        template += f"\n    has_attr(Cloud, Instance, Attribute, {actual}),"
        template += f"\n    {actual} >= Min{actual}, {actual} >= 0,"
        template += f"\n    {actual} <= Max{actual}"

    elif min_value is not None:
        template += f"\n    need_at_least(Attribute, Min{actual}),"
        template += f"\n    has_attr(Cloud, Instance, Attribute, {actual}),"
        template += f"\n    {actual} >= Min{actual}, {actual} >= 0"

    # Max value set
    else:
        template += f"\n    need_at_most(Attribute, Max{actual}),"
        template += f"\n    has_attr(Cloud, Instance, Attribute, {actual}),"
        template += f"\n    {actual} <= Max{actual}, {actual} >= 0"
    return template


def parse_value(value):
    """
    Parse a provided attribute value into an atom.

    True/False -> "true" "false"
    string     -> "string"
    """
    if isinstance(value, bool):
        value = str(value).lower()
    if isinstance(value, str):
        value = f'"{value}"'
    return value

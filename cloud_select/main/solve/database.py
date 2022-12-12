# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)


import sqlite3
from functools import partial, update_wrapper

from cloud_select.logger import logger


class with_connection:
    """
    Provide the function with a connection with open and close.

    This is used as a decorator. When added, self.conn of the
    class is instantiated for interacting with, and cleaned up
    at the end.
    """

    def __init__(self, func):
        update_wrapper(self, func)
        self.func = func

    def __get__(self, obj, objtype):
        return partial(self.__call__, obj)

    def __call__(self, cls, *args, **kwargs):
        cls.conn = cls.db.cursor()
        res = self.func(cls, *args, **kwargs)
        cls.conn.close()
        cls.conn = None
        return res


class Database:
    """
    In-memory database to query instances.
    """

    def __init__(self, filename=":memory:"):
        self.db = sqlite3.connect(filename)
        self.conn = None
        self.execute(create_instances_table)
        self.filename = filename
        # Lookup of table id to instance class
        # If too much memory, can write database to temporary file
        self.lookup = {}

    @with_connection
    def execute(self, command, fetchall=False):
        """
        Create the database, creating the instances table.
        """
        try:
            if fetchall:
                return self.conn.execute(command).fetchall()
            return self.conn.execute(command)
        except Exception as e:
            logger.exit(e)

    @with_connection
    def execute_many(self, table, items):
        """
        Create the database, creating the instances table.
        """
        if not items:
            return

        # Keys should be consistent across
        keys = list(items[0].keys())
        values = [tuple(item[x] for x in keys) for item in items]
        insert_values = ",".join(keys)
        insert_qs = ",".join("?" * len(keys))
        try:
            self.conn.executemany(
                f"insert into {table}({insert_values}) values ({insert_qs})", values
            )
        except Exception as e:
            logger.exit(e)

    def filter_instances(self, props):
        """
        Use properties to filter instances down to a desired set based.
        """
        basequery = "SELECT DISTINCT cloud, instance FROM instances"
        # No properties,
        if not props:
            return {"instance": self.execute(f"{basequery};", fetchall=True)}

        query = ""

        # Assemble rest of query
        for _, key in enumerate(props):
            if not query:
                query = basequery
            else:
                query += f"INTERSECT {basequery}"

            # Case 1: we have a range with lookup min/max
            value = props[key]

            # This returns a completed sql statement
            if key.startswith("range:"):
                value = parse_range(key, value)
            else:
                value = parse_value(value)
            query += f" WHERE {value}\n"

        logger.debug(query)
        return {"instance": self.execute(f"{query};", fetchall=True)}

    def add_instance(self, cloud_name, instance):
        """
        Generic ability to add instance to flat database
        """
        # We will do a bulk insert
        rows = []

        # Helper function to add a row - handles lists
        def add_row(item, value):
            """
            Add a row, unwrapping a list item if needed.
            """
            # Switch off and structure based on what kind of attribute we have.
            if isinstance(value, str):
                item.update({"value": value, "value_bool": None, "value_number": None})
            elif isinstance(value, bool):
                item.update(
                    {"value": None, "value_bool": int(value), "value_number": None}
                )

            # We allow a list - the instance can have more than one property
            elif isinstance(value, list):
                for v in value:
                    add_row(item, v)
                return
            else:
                item.update({"value": None, "value_bool": None, "value_number": value})
            rows.append(item)

        # Now add the rows!
        for func in instance.attribute_getters:
            value = getattr(instance, func)()
            attr = func.replace("attr_", "")
            # If we don't have data, we don't add it
            if value in [None, ""]:
                continue

            # Have instance key be name and region
            item = {"cloud": cloud_name, "instance": instance.name, "attribute": attr}
            add_row(item, value)

        self.execute_many("instances", rows)


# The table will be flat - either we have a value (text) or number but not both
# for each attribute
create_instances_table = """
CREATE TABLE IF NOT EXISTS instances (
    id integer PRIMARY KEY,
    cloud text NOT NULL,
    instance text NOT NULL,
    attribute text NOT NULL,
    value text NULLABLE,
    value_bool number NULLABLE,
    value_number number NULLABLE
);"""

# Example of foreign key
# 	FOREIGN KEY (project_id) REFERENCES projects (id)


def parse_value(key, value):
    """
    Parse a provided attribute value into an query.
    If we get here, it's not a range.

    True/False -> 1, 0
    string     -> "string"
    """
    if isinstance(value, bool):
        return (
            f"value_bool IS NOT NULL AND attribute='{key}' and value_bool={int(value)}"
        )
    if isinstance(value, str):
        return f"value IS NOT NULL AND attribute='{key}' and value='{value}'"
    if isinstance(value, (int, float)):
        return f"value_number IS NOT NULL AND attribute='{key}' and value_number={int(value)}"

    # We should not get here
    raise ValueError("A value that isn't bool or string should not be parsed.")


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

    # All of these are numbers, so we only care about value_number
    if min_value is not None and max_value is not None:
        return f"value_number IS NOT NULL AND attribute='{key}' AND value_number >= {min_value} AND value_number <= {max_value}"

    if min_value is not None:
        return f"value_number IS NOT NULL AND attribute='{key}' and value_number >= {min_value}"

    # Max value set
    return f"value_number IS NOT NULL AND attribute='{key}' and value_number <= {max_value}"

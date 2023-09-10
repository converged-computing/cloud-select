# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)


from .database import Database


class Solver:
    """
    Class to orchestrate a selection Solver.

    This originally used clingo, but since clingo doesn't support floats (yikes)
    I refactored to create an in memory database to query.
    """

    def __init__(self):
        """
        Create a solver to generate facts and rules for an ASP program.
        """
        self.db = Database()
        self.data = {}

    def add_properties(self, props):
        """
        Add properties to the setup
        """
        # These are properties we will query for
        self.data["properties"] = props

    def add_instances(self, cloud_name, instance_group):
        """
        Add cloud instances to the database
        """
        for instance in instance_group.iter_instances():
            self.db.add_instance(cloud_name, instance)

    def solve(self):
        """
        A manual solve just uses python filtering!
        """
        return self.db.filter_instances(self.data["properties"])

# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)


from .asp import PyclingoDriver, fn
from .template import write_instance_select_program


class Solver:
    """
    Class to orchestrate a selection Solver.
    """

    def __init__(self, out=None):
        """
        Create a solver to generate facts and rules for an ASP program.
        """
        self.driver = PyclingoDriver(out=out)
        self.setup = SolverSetup()

    def add_properties(self, props):
        """
        Add properties to the setup
        """
        self.setup.add_properties(props)

    def add_instances(self, cloud_name, instance_group):
        """
        Add cloud instances (as atoms) to the setup
        """
        for instance in instance_group.iter_instances():
            self.setup.add_instance(cloud_name, instance)

    def do_print(self, data, title):
        """
        Print a result to the terminal
        """
        if data:
            print("\n" + title)
            print("---------------")
            for entry in data:
                print(" " + " ".join(entry))

    def solve(self, detail=True, logic_programs=None):
        """
        Run the solve
        """
        result = self.driver.solve(self.setup, logic_programs=logic_programs)
        print("result!")
        # TODO parse result here to filter down strings, etc.
        return result.answers


class SolverSetup:
    """
    The solver setup handles parsing facts and rules.
    """

    def __init__(self):
        self.instances = {}
        self.properties = {}
        self.logic_programs = []

    def setup(self, driver):
        """
        Setup to prepare for the solve.
        This base function provides fact generation for one library.
        """
        self.gen = driver
        self.gen.h1("Cloud Select Solver")
        self.gen_instances()
        self.gen_properties()

    def add_instance(self, cloud_name, instance):
        """
        Add instance (an atom) to the solve space.
        """
        if cloud_name not in self.instances:
            self.instances[cloud_name] = []
        self.instances[cloud_name].append(instance)

    def iter_instances(self):
        """
        Flatten instances and cloud provider.
        """
        for cloud_name, instances in self.instances.items():
            for instance in instances:
                yield cloud_name, instance

    def gen_instances(self):
        """
        Generate instances
        """
        self.gen.h2("Cloud Instances")
        for cloud_name, instance in self.iter_instances():
            self.gen.fact(fn.instance(cloud_name, instance.name))
            for func in instance.attribute_getters:
                value = getattr(instance, func)()
                attr = func.replace("attr_", "")
                self.gen.fact(fn.instance_attr(cloud_name, instance.name, attr, value))

    def add_properties(self, props):
        """
        Add properties or attributes to the solve.

        Before instantiating anything, this is how we can generate a logic
        program on the fly with custom selections.
        """
        self.properties = props
        tmpfile = write_instance_select_program(props)
        self.logic_programs.append(tmpfile)

    def gen_properties(self):
        """
        Generate facts for properties.

        This currently matches exactly - need to handle min/max (range)
        """
        self.gen.h2("Properties (attributes)")
        for prop, _ in self.properties.items():
            self.gen.fact(fn.attr(prop))

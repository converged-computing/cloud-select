# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)


class Properties:
    """
    Properties from a schema to go into a solve.
    """

    def __init__(self, properties, **kwargs):
        self._allowed = properties
        self.set_properties(**kwargs)

    @property
    def defined(self):
        """
        Return defined properties.
        """
        return {k: v for k, v in self.properties.items() if v is not None}

    def set_properties(self, **kwargs):
        """
        Given an unknown set of command line arguments, parse into known
        instance properties.

        We assume that properties coming from argumnts might have a "-" instead of _.
        """
        self.properties = {
            k: v for k, v in kwargs.items() if k.replace("_", "-") in self._allowed
        }

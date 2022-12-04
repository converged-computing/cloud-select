# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)


import cloud_select.defaults as defaults
import cloud_select.main.cache as cache
import cloud_select.main.cloud as clouds
import cloud_select.main.schemas as schemas
import cloud_select.main.solve as solve
from cloud_select.logger import logger

from .settings import Settings


class Client:
    """
    Cloud select client.
    """

    def __init__(self, **kwargs):
        validate = kwargs.get("validate", True)
        self.quiet = kwargs.get("quiet", False)
        self.settings = Settings(kwargs.get("settings_file"), validate)
        self.set_clouds(kwargs.get("clouds"))

        # Set the cache and expiration
        self.cache = cache.Cache(
            kwargs.get("cache_dir") or self.settings.cache_dir or defaults.cache_dir,
            cache_expire=kwargs.get("cache_expire")
            or self.settings.cache_expire
            or defaults.cache_expire,
        )

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[cloud-select-client]"

    def set_clouds(self, listing=None):
        """
        Set client cloud classes that will be attempted.
        """
        # Reset previously init-d clouds
        self._clouds = {}
        self._cloudclass = {}
        if listing:
            for item in listing:
                item = item.lower()
                if item in clouds.cloud_names:
                    self._cloudclass[item] = clouds.clouds[item]
        else:
            self._cloudclass = clouds.clouds

    def get_clouds(self, force=False, lookup=False):
        """
        Return listing of clouds we can authenticate to, or we have data for.
        """
        # Return cached set, unless forced
        if self._clouds and not force:
            return self._clouds

        # We should always be able to get cloud classes, even without auth
        # The class knows how to parse the data types into a standard space
        for cloud_name, CloudClass in self._cloudclass.items():
            self._clouds[cloud_name] = CloudClass()
        if lookup:
            return self._clouds
        return list(self._clouds.values())

    def instances(self):
        """
        Return instances for clouds we have cached data for.

        This function does not check cache expiration, but just
        returns data we have available.
        """
        instances = {}
        for cloud in self.get_clouds():
            if self.cache.exists(cloud.name, "instances"):
                # Load instance data into the cloud
                data = self.cache.get(cloud.name, "instances")
                instances[cloud.name] = cloud.load_instances(data)
        return instances

    def update_from_cache(self, items, datatype):
        """
        Given a data type, update from the cache.
        """
        # For every cloud class we have...
        for cloud_name, cloud in self.get_clouds().items():

            # We have the data and it's expired OR we don't have it - update it
            if cloud_name not in items or self.cache.is_expired(cloud_name, datatype):
                func = getattr(cloud, datatype, None)

                # This should not happen, but let's be careful
                if not func:
                    logger.warning(
                        "Cannot call {datatype} function for cloud {cloud_name}, function is missing."
                    )
                    continue

                # Get updated items, but don't update data if we cannot (usually not authenticated)
                updated = func()
                if not updated:
                    continue
                self.cache.set(cloud_name, updated, datatype, cls=updated.Encoder)
                items[cloud_name] = updated
        return items

    def instance_select(self, max_results=20, out=None, **kwargs):
        """
        Select an instance.

        We don't currently do anything with kwargs (but will eventually to filter)
        """
        # Start with already cached data
        instances = self.update_from_cache(self.instances(), "instances")
        if not instances:
            logger.exit(
                "You don't have any clouds to search instances or cached data. Set credentials or get an offline cache."
            )

        # By here we have a lookup *by cloud) of instance groups
        # Filter down kwargs to those relevant to instances
        properties = solve.Properties(schemas.instance_properties, **kwargs)
        solver = solve.Solver(out=out)
        max_results = max_results or self.settings.max_results or 20

        # 1. write mapping of common features into functions
        # 2. filter down to desired set based on these common functions
        for cloud_name, instance_group in instances.items():
            # Generate facts for instances
            solver.add_instances(cloud_name, instance_group)
        solver.add_properties(properties.defined)

        # TODO filter down if properties include_list / exclude_list patterns defined
        # use lookup to return to user, likely add costs
        return solver.solve()

# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)


import re

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
        # The user can specify clouds on the command line or settings
        # command line takes preference!
        selection = list(set(self.settings.clouds if not listing else listing))

        # Reset previously init-d clouds
        self._clouds = {}
        self._cloudclass = {}
        if selection:
            for item in selection:
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
            return self._clouds if lookup else list(self._clouds.values())

        # We should always be able to get cloud classes, even without auth
        # The class knows how to parse the data types into a standard space
        for cloud_name, CloudClass in self._cloudclass.items():

            # Regions default to settings then defaults
            cloud_settings = getattr(self.settings, cloud_name)
            self._clouds[cloud_name] = CloudClass(
                regions=cloud_settings.get("regions"),
                cache_only=self.settings.cache_only,
            )
        return self._clouds if lookup else list(self._clouds.values())

    def instances(self):
        """
        Return instances for clouds we have cached data for.
        """
        return self.load_cache("instances")

    def prices(self):
        """
        Return instance pricing for clouds we have cached data for.
        """
        return self.load_cache("prices")

    def load_cache(self, key):
        """
        Load a named entry from the cache known to the cloud provider.

        This function does not check cache expiration, but just
        returns data we have available.
        """
        items = {}
        for cloud in self.get_clouds():
            if self.cache.exists(cloud.name, key):
                # Load data via the cloud provider
                data = self.cache.get(cloud.name, key)
                items[cloud.name] = getattr(cloud, f"load_{key}")(data)
        return items

    def update_all(self):
        """
        Update both instances and prices for all clouds defined.

        This assumes requesting a new entry the cache (items empty)
        """
        self.update_from_cache({}, "instances")
        self.update_from_cache({}, "prices")

    def update_from_cache(self, items, datatype):
        """
        Given a data type, update from the cache.
        """
        # For every cloud class we have...
        for cloud in self.get_clouds():

            # We have the data and it's expired OR we don't have it - update it
            if cloud.name not in items or self.cache.is_expired(cloud.name, datatype):
                func = getattr(cloud, datatype, None)

                # This should not happen, but let's be careful
                if not func:
                    logger.warning(
                        f"Cannot call {datatype} function for cloud {cloud.name}, function is missing."
                    )
                    continue

                # Get updated items, but don't update data if we cannot (usually not authenticated)
                updated = func()
                if not updated:
                    continue
                self.cache.set(cloud.name, updated, datatype, cls=updated.Encoder)
                items[cloud.name] = updated
        return items

    def instance_select(self, max_results=20, **kwargs):
        """
        Select an instance.
        """
        # Start with already cached data
        instances = self.update_from_cache(self.instances(), "instances")
        if not instances:
            logger.exit(
                "You don't have any clouds to search instances or cached data. Set credentials or get an offline cache."
            )

        # Only makes sense to get prices if we have instances!
        prices = {}
        if self.settings.disable_prices is not True:
            prices = self.update_from_cache(self.prices(), "prices")

        # Attributes that can't go into the solver
        region = kwargs.get("region")
        if "region" in kwargs:
            del kwargs["region"]

        # By here we have a lookup *by cloud) of instance groups
        # Filter down kwargs (properties) to those relevant to instances
        # This is not actually a solve, but it used to be and we kept the name
        properties = solve.Properties(schemas.instance_properties, **kwargs)
        solver = solve.Solver()

        # 1. write mapping of common features into functions
        # 2. filter down to desired set based on these common functions
        for cloud_name, instance_group in instances.items():

            # Do we have a request to filter by region?
            if region is not None:
                instance_group.filter_region(region)

            # Do we have prices for the cloud?
            if cloud_name in prices:
                instance_group.add_instance_prices(prices[cloud_name])

            # Generate facts for instances
            solver.add_instances(cloud_name, instance_group)

        solver.add_properties(properties.defined)

        # Select the instances!
        selected = solver.solve().get("instance") or []

        # Do we have a request for a pattern to include or exclude?
        if selected:
            for pattern in properties.include_list or []:
                selected = [x for x in selected if re.search(pattern, x)]
            for pattern in properties.exclude_list or []:
                selected = [x for x in selected if not re.search(pattern, x)]

        # Assemble back into complete data based on instance name
        return [instances[x[0]].generate_row(x[1]) for x in selected]

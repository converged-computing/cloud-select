# Copyright 2022-2023 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)


import cloudselect.cloud as clouds
import cloudselect.defaults as defaults
import cloudselect.main.cache as cache
import cloudselect.main.schemas as schemas
import cloudselect.main.solve as solve
from cloudselect.logger import logger

from .settings import Settings


class Client:
    """
    Cloud select client.
    """

    def __init__(self, **kwargs):
        validate = kwargs.get("validate", True)
        self.quiet = kwargs.get("quiet", False)
        self.settings = Settings(kwargs.get("settings_file"), validate)
        self.setup_cache(kwargs.get("use_cache"))
        self.set_clouds(kwargs.get("clouds"))

        # Keep instance groups populated with prices in sort of cache
        self.groups = None

        # Set the cache and expiration
        self.cache = cache.Cache(
            kwargs.get("cache_dir") or self.settings.cache_dir or defaults.cache_dir,
            cache_expire=kwargs.get("cache_expire")
            or self.settings.cache_expire
            or defaults.cache_expire,
        )

    def setup_cache(self, use_cache=True):
        """
        Determine if we should use the cache.

        First priority goes to flag --no-cache and then to settings.
        """
        if use_cache is None:
            use_cache = self.settings.cache_only
        self.use_cache = use_cache

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
                cache_only=self.use_cache,
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
            # Assume we don't find data
            data = None

            # Load data via the cloud provider
            if self.cache.exists(cloud.name, key) or self.cache.exists_in_memory(
                cloud.name, key
            ):
                data = self.cache.get(cloud.name, key)

            # First try - if no cache entry exists and we have ORAS support
            elif (
                not self.cache.exists(cloud.name, key)
                and self.settings.cache_oras is not None
            ):
                data = self.cache.oras_get(cloud.name, key, self.settings.cache_oras)

            # If we have data from somewhere, update our items
            if data is not None:
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
                    logger.warning(
                        f"Update function for {cloud.name} returned no results, will use previous data."
                    )
                    continue
                self.cache.set(cloud.name, updated, datatype, cls=updated.Encoder)
                items[cloud.name] = updated
        return items

    def prepare_database(self, **kwargs):
        """
        Prepare the handle to the database.

        We have this shared function to assist with dbshell.
        """
        instances = self.update_from_cache(self.instances(), "instances")
        if not instances:
            logger.exit(
                "You don't have any clouds to search instances or cached data. Set credentials or get an offline cache."
            )

        # Cut out early if we don't have attributes they need
        properties = solve.Properties(schemas.instance_properties, **kwargs)
        for cloud_name, instance_group in instances.items():
            instance_group.Instance.check_attributes(
                properties, self.settings.allow_missing_attributes
            )

        # Only makes sense to get prices if we have instances!
        prices = {}
        if self.settings.disable_prices is not True:
            prices = self.update_from_cache(self.prices(), "prices")

        # Attributes that can't go into the solver
        region = kwargs.get("region")
        if "region" in kwargs:
            del kwargs["region"]

        # Prepare the database for query
        solver = solve.Solver()

        # 1. write mapping of common features into functions
        # 2. filter down to desired set based on these common functions
        for cloud_name, instance_group in instances.items():
            # Give a warning about properties that aren't supported
            instance_group.Instance.check_attributes(
                properties, self.settings.allow_missing_attributes
            )

            # Do we have a request to filter by region?
            if region is not None:
                instance_group.filter_region(region)

            # Do we have prices for the cloud? Note prices should be added
            # first so they can be part of the query
            if cloud_name in prices:
                instance_group.add_instance_prices(prices[cloud_name])

            # Generate facts for instances
            solver.add_instances(cloud_name, instance_group)

        # Save groups so we can use them later
        self.groups = instances

        solver.add_properties(properties.defined)
        return solver

    def instance_select(self, **kwargs):
        """
        Select an instance.
        """
        solver = self.prepare_database(**kwargs)

        # Select the instances!
        # This returns a cloud and unique ID we can use to get original data
        selected = solver.solve().get("instance") or []

        # Assemble back into complete data based on instance name
        return [self.groups[x[0]].generate_row(x[1]) for x in selected]

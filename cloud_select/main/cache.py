# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

import os
import shutil
import time

import cloud_select.utils as utils
from cloud_select.logger import logger


class Cache:
    """
    Cache instances, prices, and other things.
    """

    def __init__(self, cache_dir, cache_expire=128):
        self.disable_cache = False
        if cache_expire == 0:
            self.disable_cache = True
        self.cache_dir = cache_dir
        self._cache = {}
        self._cache_expire_hours = cache_expire

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "[cloud-select-cache]"

    def clear(self, force=False):
        """
        Clear the cache (with confirmation).
        """
        if not force and not utils.confirm_action(
            "Are you sure you want to clear the cache? "
        ):
            return
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)

    def set(self, cloud_name, items, datatype, cls=None):
        """
        Given a result, cache if the user has cache enabled.

        Allow to set a custom data encoder for cloud data.
        """
        if self.disable_cache:
            return

        cache_file = self.get_cache_name(cloud_name, datatype)
        cache_dir = os.path.dirname(cache_file)

        # Ensure cache directory exists
        utils.mkdir_p(cache_dir)

        # Don't write empty data
        if not items:
            logger.warning(
                "No data found for {cloud_name} {datatype}, not writing {cache_file}."
            )
            return

        # Save to "memory" and filesystem cache
        if cloud_name not in self._cache:
            self._cache[cloud_name] = {}
        self._cache[cloud_name][datatype] = items
        utils.write_json(items, cache_file, cls=cls)
        logger.debug("{cloud_name} {datatype} written to {cache_file}.")

    def get_cache_name(self, cloud_name, name):
        """
        Return a json cache entry for a given cloud provider and data type
        """
        return os.path.join(self.cache_dir, cloud_name, f"{name}.json")

    def is_expired(self, cloud_name, datatype):
        """
        Determine if cache data is expired.
        """
        if self.disable_cache:
            return False
        cache_file = self.get_cache_name(cloud_name, datatype)
        stats = os.stat(cache_file)

        # Convert cache_expire hours to seconds
        expire_seconds = self._cache_expire_hours * 60 * 60

        # And determine if the time now since modified is greater than expire
        return (time.time() - stats.st_mtime) > expire_seconds

    def exists(self, cloud_name, datatype):
        """
        Determine if cache data exists.
        """
        if self.disable_cache:
            return False
        return os.path.exists(self.get_cache_name(cloud_name, datatype))

    def get(self, cloud_name, datatype):
        """
        Given a cache name (typically matching the endpoint) retrieve if exists.
        If provided and endpoint, wrap the result with the endpoint. Otherwise,
        return the json result.
        """
        # First effort - get from memory
        if cloud_name in self._cache and datatype in self._cache[cloud_name]:
            return self._cache[cloud_name][datatype]

        # Now look for filesystem
        cache_file = self.get_cache_name(cloud_name, datatype)
        if not os.path.exists(cache_file):
            return

        # Load the cache, reset if error loading (invalid json)
        try:
            return utils.read_json(cache_file)
        except Exception as e:
            logger.warning(f"Cache entry {cache_file} has corrupt json: {e}, removing.")
            os.remove(cache_file)

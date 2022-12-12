# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

import os
import shutil
import time
from datetime import datetime

import cloud_select.main.oras as oras
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
        self._oras_manifest = None

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
                f"No data found for {cloud_name} {datatype}, not writing {cache_file}."
            )
            return

        self.memory_set(cloud_name, items, datatype)
        utils.write_json(items, cache_file, cls=cls)
        logger.debug(f"{cloud_name} {datatype} written to {cache_file}.")

    def memory_set(self, cloud_name, items, datatype):
        """
        Set the cache only to the instance (e.g., in memory)
        """
        # Save to "memory" and filesystem cache
        if cloud_name not in self._cache:
            self._cache[cloud_name] = {}
        self._cache[cloud_name][datatype] = items

    def get_cache_name(self, cloud_name, name):
        """
        Return a json cache entry for a given cloud provider and data type
        """
        # Enforce using web prices for now.
        if cloud_name == "google" and name == "prices":
            name = "prices-web"
        return os.path.join(self.cache_dir, cloud_name, f"{name}.json")

    def push(self, uri):
        """
        Given an ORAS identifier, save cache to it.
        """
        oras_cli = oras.get_oras_client(require_auth=True)

        # Create lookup of archives - relative path and mediatype
        archives = []
        now = datetime.now()
        for filename in self.iter_cache(relative=True):
            cloud = os.path.basename(os.path.dirname(filename))
            datatype = os.path.basename(filename).split(".")[0]
            media_type = f"org.llnl.gov.cloud-select.{cloud}.{datatype}"
            size = os.path.getsize(os.path.join(self.cache_dir, filename))  # bytes
            annotations = {"creationTime": str(now), "size": str(size)}
            archives.append(
                {
                    "path": filename,
                    "title": filename,
                    "media_type": media_type,
                    "annotations": annotations,
                }
            )

        # Push should be relative to cache context
        with utils.workdir(self.cache_dir):
            oras_cli.push(uri, archives)

    def iter_cache(self, relative=False):
        """
        Yield json paths in the cache, either absolte or relative paths.
        """
        for filename in utils.recursive_find(self.cache_dir):
            if not filename.endswith("json"):
                continue
            if relative:
                yield filename.replace(self.cache_dir, "").strip(os.sep)
            else:
                yield filename

    def is_expired(self, cloud_name, datatype):
        """
        Determine if cache data is expired.
        """
        # If the cache is disabled or already using memory, exit early
        if self.disable_cache or self.exists_in_memory(cloud_name, datatype):
            return False

        cache_file = self.get_cache_name(cloud_name, datatype)

        # One off tweak to use Google Cloud web prices temporarily
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

    def exists_in_memory(self, cloud_name, datatype):
        """
        Determine if we are using a memory cache and have it loaded
        """
        if cloud_name in self._cache and self._cache[cloud_name].get(datatype):
            return True
        return False

    def oras_get(self, cloud_name, datatype, package):
        """
        Update the cache from an ORAS package.

        Given a known ORAS (OCI Registry as Storage) package, get an entry
        from it. We retrieve the manifest and cache it for later use, and only
        download if the data file is needed (more efficient).
        """
        oras_cli = oras.get_oras_client(require_auth=True)
        # Update our manifest if we don't have one yet
        if not self._oras_manifest:
            try:
                self._oras_manifest = oras_cli.get_manifest(package)
            except Exception:
                logger.warning(
                    f"Issue getting manifest for {package}, check the image and tag name. No cache update from ORAS"
                )
                return

        # Download the layer to the cache directory and return the filename
        # The oras package paths are relative to a root, so we use the cache root
        datafile = oras_cli.download_layer(
            cloud_name,
            datatype,
            manifest=self._oras_manifest,
            root=self.cache_dir,
            package=package,
        )
        logger.debug(f"Found oras package data file {datafile}")
        if datafile:
            return utils.read_json(datafile)

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
        # This is a temporary hack to allow Google prices to be prices-web.json
        cache_file = self.get_cache_name(cloud_name, datatype)
        if not os.path.exists(cache_file):
            return

        # Load the cache, reset if error loading (invalid json)
        try:
            return utils.read_json(cache_file)
        except Exception as e:
            logger.warning(f"Cache entry {cache_file} has corrupt json: {e}, removing.")
            os.remove(cache_file)

# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

import re
import time

from cloud_select.logger import logger

from ..base import CloudProvider
from .instance import GoogleCloudInstanceGroup
from .prices import GoogleCloudPrices


class GoogleCloud(CloudProvider):
    """
    A Google Cloud provider wrapper

    We allow the client init to proceed given authentication is not
    possible as it can provide data served from a cache, wrapping
    available instances.
    """

    name = "google"

    def __init__(self, **kwargs):
        self.regions = kwargs.get("regions") or ["us-east1", "us-west1", "us-central1"]
        self.project = None
        self.compute_cli = None
        self.billing_cli = None
        try:
            self._set_services(kwargs.get("cache_only"))
        except Exception as e:
            logger.debug(f"Cannot create Google Cloud clients {e}")
            self.has_auth = False
        super(GoogleCloud, self).__init__()

    def prices(self):
        """
        Use the API to retrieve and return prices to cache.
        """
        if not self.has_auth:
            return self.fail_message("prices, authentication not set.")

        # Get services first - there are almost 2k! Look for compute engine
        logger.info(
            f"Retrieving prices for {self.name} - this might take a few minutes."
        )
        services = self._retry_request(self.billing_cli.services().list())
        services = [
            x for x in services["services"] if x["displayName"] == "Compute Engine"
        ]

        # Bail out if we don't have one service
        if len(services) != 1:
            return self.fail_message("prices, cannot find Compute Engine service.")

        # We want to add "global" to our regions to search
        regions = self.regions + ["global"]

        # Get metadata about compute (ALL prices here) and handle nextPage tokens
        # https://cloud.google.com/billing/docs/reference/rest/v1/services.skus/list
        # There are millions of prices - we will filter down to compute engine
        # instances, but this first call still takes a long time. I think this
        # could be hugely helped if we are able to provide a cache of filtered prices.
        # The default currency returned is dollars (USD).
        prices = []
        page_token = None
        while True:
            items = self._retry_request(
                self.billing_cli.services()
                .skus()
                .list(parent=services[0]["name"], pageToken=page_token)
            )

            # We can only reasonably save entries from our service regions of interest
            prices += [
                sku
                for sku in items.get("skus", [])
                if any(x in sku["serviceRegions"] for x in regions)
            ]
            print(f"{len(prices)} total results...", end="\r")
            if not items.get("nextPageToken"):
                break
            page_token = items["nextPageToken"]

        # Handle pagination
        return self.load_prices(prices)

    def instances(self):
        """
        Use the API to retrieve (and return) instances within a set of regions.
        """
        if not self.has_auth:
            return self.fail_message("instances, authentication not set.")

        logger.info(f"Retrieving instances for {self.name}")

        # Regular expression to determine if zone in region
        regexp = "^(%s)" % "|".join(self.regions)

        # Retrieve zones, filter down to selected regions
        zones = self._retry_request(self.compute_cli.zones().list(project=self.project))
        zones = [z for z in zones["items"] if re.search(regexp, z["name"])]

        # Retrieve machine types available in zones.
        # https://cloud.google.com/compute/docs/regions-zones/
        machine_types = []
        for zone in zones:
            request = self.compute_cli.machineTypes().list(
                project=self.project, zone=zone["name"]
            )
            machine_types += self._retry_request(request)["items"]

        # Get accelerator types (for GPU) to add to them?
        # TODO - I don't see where we can get memory for GPUs :(
        # https://cloud.google.com/compute/docs/reference/rest/v1/acceleratorTypes
        # accels = self._retry_request(self.compute_cli.acceleratorTypes().aggregatedList(project=self.project))

        # Return a wrapped set of instances
        return self.load_instances(machine_types)

    def load_prices(self, data):
        """
        Load prices data from json instal class
        """
        return GoogleCloudPrices(data)

    def load_instances(self, data):
        """
        Load instance data from json.
        """
        return GoogleCloudInstanceGroup(data)

    def _set_services(self, cache_only=False):
        """
        Use Google Discovery Build to generate an API client for compute and billing.
        """
        if cache_only is True:
            self.has_auth = False
            return
        import google.auth
        import google_auth_httplib2
        import googleapiclient
        import httplib2
        from googleapiclient.discovery import build as discovery_build

        # Get default credentials. If there is an exception, caught by init function
        # google.auth.DefaultCredentialsError
        creds, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        self.project = project

        def build_request(_, *args, **kwargs):
            """
            See https://googleapis.github.io/google-api-python-client/docs/thread_safety.html

            Note that the first positional arg (http) is required despite not being used here.
            """
            new_http = google_auth_httplib2.AuthorizedHttp(creds, http=httplib2.Http())
            return googleapiclient.http.HttpRequest(new_http, *args, **kwargs)

        # Discovery client for Google Cloud Compute
        # https://cloud.google.com/compute/docs/reference/rest/v1/instances
        authorized_http = google_auth_httplib2.AuthorizedHttp(creds)
        self.compute_cli = discovery_build(
            "compute",
            "v1",
            cache_discovery=False,
            http=authorized_http,
            requestBuilder=build_request,
        )
        self.billing_cli = discovery_build(
            "cloudbilling",
            "v1",
            cache_discovery=False,
            http=authorized_http,
            requestBuilder=build_request,
        )
        self.has_auth = True

    def _retry_request(self, request, timeout=2, attempts=3):
        """
        The Google Python API client frequently has BrokenPipe errors. This
        function takes a request, and executes it up to number of retry,
        each time with a 2* increase in timeout.
        """
        import googleapiclient

        try:
            return request.execute()
        except BrokenPipeError as e:
            if attempts > 0:
                time.sleep(timeout)
                return self._retry_request(
                    request, timeout=timeout * 2, attempts=attempts - 1
                )
            raise e
        except googleapiclient.errors.HttpError as e:
            if attempts > 0:
                time.sleep(timeout)
                return self._retry_request(
                    request, timeout=timeout * 2, attempts=attempts - 1
                )
            raise e
        except Exception as e:
            if attempts > 0:
                time.sleep(timeout)
                return self._retry_request(
                    request, timeout=timeout * 2, attempts=attempts - 1
                )
            raise e

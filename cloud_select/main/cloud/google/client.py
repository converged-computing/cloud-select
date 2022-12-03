# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

import re
import time

from cloud_select.logger import logger

from ..base import CloudProvider
from .instance import GoogleCloudInstanceGroup


class GoogleCloud(CloudProvider):
    """
    A Google Cloud provider wrapper

    We allow the client init to proceed given authentication is not
    possible as it can provide data served from a cache, wrapping
    available instances.
    """

    name = "google"

    def __init__(self, **kwargs):

        # TODO allow setting of regions from settings or client
        self.regions = ["us-east1", "us-west1", "us-central1"]
        self.project = None
        self.compute_cli = None

        try:
            self._set_services()
        except Exception as e:
            logger.warning(f"Unable to authenticate to Google Cloud: {e}")
            self.has_auth = False
        super(GoogleCloud, self).__init__()

    def instances(self):
        """
        Use the API to retrieve (and return) instances within a set of regions.
        """
        if not self.has_auth:
            logger.info(
                f"Cannot retrieve instances for {self.name}, authentication not set."
            )
            return []
        logger.info(f"Retrieving instances for {self.name}")

        # Regular expression to determine if zone in region
        regexp = "^(%s)" % "|".join(self.regions)

        # Retrieve zones, filter down to selected regions
        zones = self._retry_request(self.compute_cli.zones().list(project=self.project))
        zones = [z for z in zones["items"] if re.search(regexp, z["name"])]

        # Retrieve machine types available across zones
        # https://cloud.google.com/compute/docs/regions-zones/
        machine_types = []
        for zone in zones:
            request = self.compute_cli.machineTypes().list(
                project=self.project, zone=zone["name"]
            )
            machine_types += self._retry_request(request)["items"]

        # Return a wrapped set of instances
        return self.load_instances(machine_types)

    def load_instances(self, data):
        """
        Load instance data from json.
        """
        return GoogleCloudInstanceGroup(data)

    def _set_services(self):
        """
        Use Google Discovery Build to generate an API client for compute.
        """
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

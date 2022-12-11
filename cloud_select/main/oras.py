# Copyright 2022 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)

import os

import oras.defaults
import oras.oci
import oras.provider
import oras.utils
from oras.decorator import ensure_container

import cloud_select.defaults as defaults
from cloud_select.logger import logger


def get_oras_client(require_auth=False):
    """
    Consistent method to get an oras client
    """
    user = os.environ.get("ORAS_USER")
    password = os.environ.get("ORAS_PASS")
    reg = Registry()
    if user and password:
        logger.debug("Found username and password for basic auth")
        reg.set_basic_auth(user, password)
    else:
        logfunc = logger.exit if require_auth else logger.warning
        logfunc("ORAS_USER or ORAS_PASS is missing, push may have issues.")
    return reg


def pull_to_dir(pull_dir, target):
    """
    Given a URI, pull to an output directory.
    """
    reg = get_oras_client()
    return reg.pull(target=target, outdir=pull_dir)


class Registry(oras.provider.Registry):
    def download_layer(self, cloud_name, datatype, manifest, root, package):
        """
        Given a manifest of layers, retrieve a layer based on cloud and content type.

        E.g., org.llnl.gov.cloud-select.google.prices (google and prices). The
        oras artifacts are pushed with relative paths to the cache root,
        so we can extract them directly to the root path plus their OCI annotation
        for the artifact title.
        """
        # Find the layer of interest! Currently we look for presence of the string
        # e.g., "prices" can come from "prices" or "prices-web"
        for layer in manifest.get("layers", []):

            # E.g., google.prices or google.prices-web or aws.prices
            contents = layer["mediaType"].split("cloud-select.")[-1]
            cloud_found, data_found = contents.split(".")
            if cloud_found != cloud_name:
                continue

            # This gives flexibility to support different variances of prices, etc.
            if datatype in data_found:

                logger.info(f"Downloading data file for {datatype} from ORAS cache...")
                artifact = layer["annotations"]["org.opencontainers.image.title"]

                # Assemble output file name in root
                outfile = oras.utils.sanitize_path(root, os.path.join(root, artifact))

                # download blob ensures we stream, otherwise _get_blob would return request
                # this function also handles creating the output directory if does not exist
                return self.download_blob(package, layer["digest"], outfile)

    @ensure_container
    def push(self, container, archives: list):
        """
        Given a list of layer metadata (paths and corresponding mediaType) push.
        """
        # Prepare a new manifest
        manifest = oras.oci.NewManifest()

        # Upload files as blobs
        for item in archives:

            blob = item.get("path")
            media_type = item.get("media_type") or defaults.default_media_type
            annots = item.get("annotations", {})

            if not blob or not os.path.exists(blob):
                logger.warning(f"Path {blob} does not exist or is not defineds.")
                continue

            # Artifact title is basename or user defined
            blob_name = item.get("title") or os.path.basename(blob)

            # If it's a directory, we need to compress
            cleanup_blob = False
            if os.path.isdir(blob):
                blob = oras.utils.make_targz(blob)
                cleanup_blob = True

            # Create a new layer from the blob
            layer = oras.oci.NewLayer(blob, media_type, is_dir=cleanup_blob)
            logger.debug(f"Preparing layer {oras.utils.print_json(layer)}")

            # Update annotations with title we will need for extraction
            annots.update({oras.defaults.annotation_title: blob_name})
            layer["annotations"] = annots

            # update the manifest with the new layer
            manifest["layers"].append(layer)

            # Upload the blob layer
            logger.info(f"Uploading {blob} to {container.uri}")
            response = self._upload_blob(blob, container, layer)
            self._check_200_response(response)

            # Do we need to cleanup a temporary targz?
            if cleanup_blob and os.path.exists(blob):
                os.remove(blob)

        # Prepare manifest and config
        manifest["annotations"] = defaults.default_manifest_annotations
        conf, config_file = oras.oci.ManifestConfig()
        conf["annotations"] = defaults.default_config_annotations

        # Config is just another layer blob!
        response = self._upload_blob(config_file, container, conf)
        self._check_200_response(response)

        # Final upload of the manifest
        manifest["config"] = conf
        self._check_200_response(self.upload_manifest(manifest, container))
        print(f"Successfully pushed {container}")
        return response

# Copyright 2022-2023 Lawrence Livermore National Security, LLC and other
# HPCIC DevTools Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (MIT)


import cloudselect.cloud as clouds
import cloudselect.defaults as defaults
import cloudselect.utils as utils
from cloudselect.logger import logger

from .client import Client


class InstanceSelector:
    """
    Cloud selector.

    A selector is intended to wrap the Client, and be used inside other Python
    tools to provide interfaces for people to query and select.
    """

    def __init__(self, cloud, regions=None):
        """
        Create a cloud select client, optionally filtering
        to regions and/or clouds.
        """
        if cloud not in clouds.cloud_names:
            raise ValueError(
                f"{cloud} is not a known cloud, choose from {clouds.cloud_names}"
            )
        self.cloud = cloud
        self.cli = Client(clouds=[cloud])

        # These are cloud specific settings
        self.settings = getattr(self.cli.settings, cloud, {}) or {}
        self.regions = regions

    def select_instance(
        self,
        resources,
        default=None,
        interactive=True,
        allow_exit=True,
        sort_by="price",
        ascending=True,
    ):
        """
        Select an instance based on a dict of known resources.
        """
        instance = None
        if sort_by not in defaults.sort_by_fields:
            raise ValueError(
                f"{sort_by} is not a valid field to sort by. Options are {defaults.sort_by_fields}"
            )
        # If we don't have matching regions for prices in cache, no go
        if self.regions and not any(
            x for x in self.regions if x in self.settings["regions"]
        ):
            return default

        # We use flexible by default - the smallest usually are priority on list (cheaper)
        logger.info("👀️ Looking for instances...")

        instances = self.cli.instance_select(**resources)
        subset = [x for x in instances if x.get(sort_by) not in [None, ""]]

        # If sort by price, need to set price to be float
        if sort_by == "price":
            for item in subset:
                if sort_by not in item:
                    continue
                item[sort_by] = float(item[sort_by])

        selection = sorted(subset, key=lambda x: x[sort_by], reverse=not ascending)

        # If not interactive, just return selection
        if not interactive:
            return selection if selection else default

        # This can likely be standardized when we implement for other clouds
        if selection:
            prompt = "Please choose an instance type, these are sorted by price, least to greatest."
            options = self.get_options(selection, default, allow_exit)
            _, index = utils.choose(options, prompt)

            # If we chose the last one, exit
            if index == len(options) - 1 and allow_exit:
                logger.exit("Exiting on request.")

            # Only set index if we didn't choose a default
            if (default and index != 0) or not default:
                instance = selection[index]["name"]

        if not instance:
            instance = default
            logger.info(f"Falling back to default instance {instance}")

        return instance

    def get_options(
        self,
        selection,
        default=None,
        allow_exit=True,
    ):
        """
        Get options for cloud select
        """
        options = []
        if default:
            options = [f"     Use default {default}"]

        for instance in selection:
            name = instance["name"].rjust(15)
            description = instance["description"].ljust(5)
            option = f"{name} {description} at {instance['price']} $/hour"
            options.append(option)

        options += [
            f"{x['name'].rjust(15)} {x['description']} at {x['price']} $/hour"
            for x in selection
        ]
        if allow_exit:
            options.append("     Exit and start over")
        return options

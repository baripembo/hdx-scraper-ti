#!/usr/bin/python
"""ti scraper"""

import logging
from typing import List, Optional

from hdx.api.configuration import Configuration
from hdx.data.dataset import Dataset
from hdx.data.hdxobject import HDXError
from hdx.utilities.base_downloader import DownloadError
from hdx.utilities.retriever import Retrieve

logger = logging.getLogger(__name__)


class TI:
    def __init__(self, configuration: Configuration, retriever: Retrieve, temp_dir: str):
        self._configuration = configuration
        self._retriever = retriever
        self._temp_dir = temp_dir
        self.data_url = self._configuration["base_url"]

    def get_data(self) -> List:
        base_url = self._configuration["base_url"]

        try:
            content = self._retriever.download_json(base_url, "cpi")
            print("content", content)
        except DownloadError as e:
            logger.error(f"Could not get data from {self.data_url} {e}")
            return []

        return content

    def generate_dataset(self) -> Optional[Dataset]:
        # To be generated
        dataset_name = None
        dataset_title = None
        dataset_time_period = None
        dataset_tags = None
        dataset_country_iso3 = None

        # Dataset info
        dataset = Dataset(
            {
                "name": dataset_name,
                "title": dataset_title,
            }
        )

        dataset.set_time_period(dataset_time_period)
        dataset.add_tags(dataset_tags)
        # Only if needed
        # dataset.set_subnational(True)
        try:
            dataset.add_country_location(dataset_country_iso3)
        except HDXError:
            logger.error(f"Couldn't find country {dataset_country_iso3}, skipping")
            return

        # Add resources here

        return dataset

#!/usr/bin/python
"""Transparency International scraper"""

import logging
from typing import List, Tuple

from hdx.api.configuration import Configuration
from hdx.data.dataset import Dataset
from hdx.data.showcase import Showcase
from hdx.utilities.base_downloader import DownloadError
from hdx.utilities.retriever import Retrieve
from slugify import slugify

logger = logging.getLogger(__name__)


class TI:
    def __init__(self, configuration: Configuration, retriever: Retrieve, temp_dir: str):
        self._configuration = configuration
        self._retriever = retriever
        self._temp_dir = temp_dir

    def get_data(self) -> List:
        base_url = self._configuration["base_url"]

        try:
            data = self._retriever.download_json(base_url, "cpi.json")
        except DownloadError as e:
            logger.error(f"Could not get data from {base_url} {e}")
            return {}
        print(data)
        return data

    def format_data(self, data: List) -> dict:
        yearly_data = {}

        for row in data:
            year = row["year"]
            if year not in yearly_data:
                yearly_data[year] = []
            yearly_data[year].append(row)

        years_order = {
            year: yearly_data[year] for year in sorted(yearly_data.keys(), reverse=True)
        }
        return years_order

    def get_date_range(self, data: List) -> dict:
        """
        Get min and max dates from dataset
        """
        # Convert reported_date to datetime object
        dates = []
        for row in data:
            date_year = row.get("year")
            if date_year:
                try:
                    dates.append(date_year)
                except ValueError as e:
                    print(f"Error parsing date '{date_year}': {e}")

        min_date = min(dates)
        max_date = max(dates)

        return {"min_date": min_date, "max_date": max_date}

    def generate_dataset(self) -> Tuple[Dataset, Showcase]:
        data = self.get_data()

        dataset_info = self._configuration
        dataset_title = f"{dataset_info['title']}"
        slugified_name = slugify(dataset_title)

        # Create dataset
        dataset = Dataset({"name": slugified_name, "title": dataset_title})

        # Add dataset info
        dataset.add_other_location("world")
        dataset.add_tags(self._configuration["tags"])
        date_range = self.get_date_range(data)
        dataset.set_time_period_year_range(date_range["min_date"], date_range["max_date"])

        # Create resource
        resource_name = f"{slugified_name}.csv"
        resource_description = dataset_info["description"].replace("[year]", "")
        resource = {"name": resource_name, "description": resource_description}

        dataset.generate_resource_from_rows(
            self._temp_dir, resource_name, data, resource, list(data[0].keys())
        )

        # Add resources
        data_by_year = self.format_data(data)
        for year, rows in data_by_year.items():
            # Create resource
            resource_name = f"{slugified_name}-{year}.csv"
            resource_description = dataset_info["description"].replace("[year]", str(year))
            resource = {"name": resource_name, "description": resource_description}

            dataset.generate_resource_from_rows(
                self._temp_dir, resource_name, rows, resource, list(rows[0].keys())
            )

        # Showcase
        showcase = Showcase(
            {
                "name": f"{slugified_name}-showcase",
                "title": dataset_info["showcase_title"],
                "notes": dataset_info["showcase_notes"],
                "url": dataset_info["showcase_url"],
                "image_url": dataset_info["showcase_image_url"],
            }
        )
        showcase.add_tags(self._configuration["tags"])

        return dataset, showcase

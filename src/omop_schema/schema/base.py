import os
from abc import ABC, abstractmethod

import pyarrow as pa
from pyarrow import csv


class OMOPSchemaBase(ABC):
    """
    Abstract base class to define and manage the schema for OMOP CDM tables.
    """

    def __init__(self):
        self.schemas = self._load_schema()

    @abstractmethod
    def _load_schema(self):
        """
        Load the schema for the OMOP CDM tables.
        This method should be implemented by subclasses.
        """

    def get_schema(self, table_name):
        return self.schemas.get(table_name, {})

    def get_pyarrow_schema(self, table_name):
        """
        Get the PyArrow schema for a specific table.

        Args:
            table_name (str): The name of the table.

        Returns:
            pyarrow.Schema: The PyArrow schema for the specified table.
        """
        return pa.schema(
            [pa.field(name, dtype) for name, dtype in self.get_schema(table_name).items()]
        )

    def get_table_names(self):
        return list(self.schemas.keys())

    def load_csv_dataset(self, folder_path):
        """
        Load datasets from a folder, matching files to table schemas.

        Args:
            folder_path (str): Path to the folder containing the dataset files.

        Returns:
            dict: A dictionary where keys are table names and values are PyArrow tables.
        """
        datasets = {}
        for file_name in os.listdir(folder_path):
            table_name, ext = os.path.splitext(file_name)
            if ext.lower() == ".csv" and table_name in self.get_table_names():
                file_path = os.path.join(folder_path, file_name)
                table_schema = pa.schema(
                    [pa.field(name, dtype) for name, dtype in self.get_schema(table_name).items()]
                )
                try:
                    datasets[table_name] = csv.read_csv(
                        file_path,
                        read_options=csv.ReadOptions(),
                        convert_options=csv.ConvertOptions(column_types=table_schema),
                    )
                except Exception as e:
                    print(f"Error loading {file_name}: {e}")
        return datasets

    # def read_csv(self, file_path, table_name):
    #     schema = self.get_schema(table_name)
    #     return #pl.read_csv(file_path, dtypes=schema)

import pyarrow as pa
import pyarrow.parquet as pq
from src.omop_schema.base import OMOPSchemaBase


class OMOPValidator:
    def __init__(self, schema_version):
        self.schema = schema_version()._load_schema()

    def validate_table(self, table_name, dataset):
        """
        Validate a dataset against the schema for a specific OMOP table.

        Args:
            table_name (str): The name of the OMOP table to validate.
            dataset (pa.Table): The dataset to validate.

        Returns:
            dict: Validation results with missing and mismatched columns.
        """
        if table_name not in self.schema:
            raise ValueError(f"Table '{table_name}' is not defined in the schema.")

        expected_schema = self.schema[table_name]
        dataset_schema = {field.name: field.type for field in dataset.schema}

        missing_columns = [col for col in expected_schema if col not in dataset_schema]
        mismatched_columns = [
            col for col in expected_schema
            if col in dataset_schema and dataset_schema[col] != expected_schema[col]
        ]

        return {
            "missing_columns": missing_columns,
            "mismatched_columns": mismatched_columns,
        }


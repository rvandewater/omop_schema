try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    PANDAS_AVAILABLE = False

try:
    import polars as pl
    POLARS_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    POLARS_AVAILABLE = False
import pyarrow as pa

from .utils import (
    get_table_path,
    load_table_polars,
    pyarrow_to_polars_schema,
)


class OMOPValidator:
    def __init__(self, schema_version):
        self.schema_version = schema_version()
        self.schema = schema_version()._load_schema()

    def get_schema_version(self):
        """
        Get the schema for the specified OMOP version.

        Returns:
            OMOPSchemaBase: The schema for the specified OMOP version.
        """
        return self.schema_version

    def validate_table(self, table_name, dataset):
        """
        Validate a dataset against the schema for a specific OMOP table.

        Args:
            table_name (str): The name of the OMOP table to validate.
            dataset (pa.Table | pl.DataFrame | pl.LazyFrame | pd.DataFrame): The dataset to validate.

        Returns:
            dict: Validation results with missing, mismatched, extra columns, and correct columns.
        """
        if table_name not in self.schema:
            raise ValueError(f"Table '{table_name}' is not defined in the schema.")

        expected_schema = self.schema[table_name]
        # Extract schema based on dataset type
        if isinstance(dataset, pa.Table):
            dataset_schema = {field.name: field.type for field in dataset.schema}
        elif POLARS_AVAILABLE and isinstance(dataset, (pl.DataFrame, pl.LazyFrame)):
            expected_schema = pyarrow_to_polars_schema(pa.schema(expected_schema))
            dataset_schema = dataset.collect_schema()
            # dataset_schema = {col: dataset.schema[col] for col in dataset.columns}
        elif PANDAS_AVAILABLE and isinstance(dataset, pd.DataFrame):
            dataset_schema = {col: str(dtype) for col, dtype in dataset.dtypes.items()}
        else:
            raise TypeError(
                "Unsupported dataset type. Must be pa.Table, pl.DataFrame, pl.LazyFrame, or pd.DataFrame."
            )

        # Validation logic
        missing_columns = [
            (col, expected_schema[col]) for col in expected_schema if col not in dataset_schema
        ]
        mismatched_columns = [
            (col, dataset_schema[col], expected_schema[col])
            for col in expected_schema
            if col in dataset_schema and dataset_schema[col] != expected_schema[col]
        ]
        extra_columns = [(col, dataset_schema[col]) for col in dataset_schema if col not in expected_schema]
        correct_columns = [
            (col, expected_schema[col])
            for col in expected_schema
            if col in dataset_schema and dataset_schema[col] == expected_schema[col]
        ]

        return {
            "missing_columns": missing_columns,
            "mismatched_columns": mismatched_columns,
            "extra_columns": extra_columns,
            "correct_columns": correct_columns,
        }

    def strictly_valid(self):
        """
        Check if the dataset is strictly valid according to the schema.

        Returns:
            bool: True if the dataset is strictly valid, False otherwise.
        """
        for table_name, expected_schema in self.schema.items():
            dataset = self.load_dataset(table_name)
            validation_result = self.validate_table(table_name, dataset)
            if (
                validation_result["missing_columns"]
                or validation_result["mismatched_columns"]
                or validation_result["extra_columns"]
            ):
                return False
        return True

    def base_valid(self):
        """
        Check if the dataset is base valid according to the schema. Excludes checking for extra columns.

        Returns:
            bool: True if the dataset is base valid, False otherwise.
        """
        for table_name, expected_schema in self.schema.items():
            dataset = self.load_dataset(table_name)
            validation_result = self.validate_table(table_name, dataset)
            if validation_result["missing_columns"] or validation_result["mismatched_columns"]:
                return False
        return True


import logging
from rich.console import Console
from rich.table import Table

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def validate_omop_dataset_graphically(validator, dataset_path, load_with_expected_schema=True):
    """
    Validate an OMOP dataset and display the results in a rich table format with logging.
    """
    console = Console(width=300, force_terminal=True)
    results_table = Table(title="OMOP Dataset Validation Results")

    results_table.add_column("Table Name", style="bold")
    results_table.add_column("Missing Columns (Name: Expected Type)", style="red")
    results_table.add_column("Mismatched Columns (Name: Actual Type -> Expected Type)", style="yellow")
    results_table.add_column("Extra Columns (Name: Actual Type)", style="green")
    results_table.add_column("Correct Columns (Name: Type)", style="cyan")

    for table_name in validator.schema.keys():
        logger.info(f"Validating table: {table_name}")
        console.log(f"[bold blue]Validating table: {table_name}[/bold blue]")

        table_path = get_table_path(dataset_path, table_name)
        if table_path is None:
            message = f"Table '{table_name}' does not exist in this dataset."
            logger.warning(message)
            results_table.add_row(table_name, "[red]Table does not exist in this dataset[/red]", "-", "-", "-")
            continue

        expected_schema = validator.get_schema_version()
        dataset = load_table_polars(table_path, expected_schema if load_with_expected_schema else None)
        if dataset is not None:
            result = validator.validate_table(table_name, dataset)
        else:
            message = f"Table '{table_name}' could not be loaded."
            logger.warning(message)
            results_table.add_row(table_name, "[red]Table could not be loaded[/red]", "-", "-", "-")
            continue

        missing_columns = (
            ", ".join(f"{col}: {expected}" for col, expected in result["missing_columns"])
            if result["missing_columns"]
            else "None"
        )
        mismatched_columns = (
            ", ".join(
                f"{col}: {actual} -> {expected}" for col, actual, expected in result["mismatched_columns"]
            )
            if result["mismatched_columns"]
            else "None"
        )
        extra_columns = (
            ", ".join(f"{col}: {actual}" for col, actual in result["extra_columns"])
            if result["extra_columns"]
            else "None"
        )
        correct_columns = (
            ", ".join(f"{col}: {expected}" for col, expected in result["correct_columns"])
            if result["correct_columns"]
            else "None"
        )

        logger.info(f"Validation results for table '{table_name}': Missing: {missing_columns}, "
                    f"Mismatched: {mismatched_columns}, Extra: {extra_columns}, Correct: {correct_columns}")
        console.log(f"[green]Validation completed for table: {table_name}[/green]")

        results_table.add_row(table_name, missing_columns, mismatched_columns, extra_columns, correct_columns)

    console.print(results_table)
    logger.info("Validation process completed.")

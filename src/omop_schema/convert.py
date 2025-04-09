import os

import pyarrow as pa


def convert_to_schema(dataset, target_schema, allow_extra_columns=False):
    """
    Convert a dataset to match the target schema.

    Args:
        dataset (pa.Table): The input dataset with a potentially different schema.
        target_schema (pa.Schema): The desired schema to align the dataset to.
        allow_extra_columns (bool): If True, extra columns in the dataset are retained.

    Returns:
        pa.Table: The dataset converted to match the target schema.
    """
    # Add missing columns with default values
    missing_columns = [field for field in target_schema if field.name not in dataset.schema.names]
    for field in missing_columns:
        default_value = pa.array([None] * dataset.num_rows, type=field.type)
        dataset = dataset.append_column(field.name, default_value)

    # If extra columns are not allowed, drop them
    if not allow_extra_columns:
        dataset = dataset.select([field.name for field in target_schema])

    # Ensure column types match the target schema
    columns = []
    for field in target_schema:
        column = dataset[field.name]
        if column.type != field.type:
            column = column.cast(field.type)
        columns.append(column)

    # Include extra columns if allowed
    if allow_extra_columns:
        extra_columns = [dataset[name] for name in dataset.schema.names if name not in target_schema.names]
        columns.extend(extra_columns)

    return pa.Table.from_arrays(columns, schema=target_schema)


try:
    import polars as pl

    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False


def convert_to_schema_polars(dataset, target_schema, allow_extra_columns=False, allow_missing_columns=True):
    """
    Convert a Polars DataFrame or LazyFrame to match the target schema.

    Args:
        dataset (pl.DataFrame or pl.LazyFrame): The input dataset with a potentially different schema.
        target_schema (dict): A dictionary defining the desired schema (column name -> data type).
        allow_extra_columns (bool): If True, extra columns in the dataset are retained.
        allow_missing_columns (bool): If True, missing columns in the dataset are added with default values.

    Returns:
        pl.DataFrame or pl.LazyFrame: The dataset converted to match the target schema.
    """
    # Ensure the dataset is either a DataFrame or LazyFrame
    if not isinstance(dataset, (pl.DataFrame, pl.LazyFrame)):
        raise TypeError("Dataset must be a Polars DataFrame or LazyFrame.")

    source_schema = dataset.collect_schema()

    # Add missing columns with default values
    for column, dtype in target_schema.items():
        if column not in source_schema.names():
            default_value = pl.lit(None, dtype=dtype).alias(column)
            dataset = dataset.with_columns(default_value)

    # If extra columns are not allowed, select only the target schema columns
    if not allow_extra_columns:
        dataset = dataset.select(list(target_schema.keys()))

    # Ensure column types match the target schema


    if not allow_missing_columns:
        missing_columns = [
            column for column in target_schema if column not in source_schema.names()
        ]
        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}")

    for column, dtype in target_schema.items():
        if column not in source_schema:
            continue
        if source_schema.get(column) != dtype:
            dataset = dataset.with_columns(pl.col(column).cast(dtype))

    return dataset

def process_omop_dataset(input_dir, output_dir, schema):
    """
    Reads an OMOP dataset from CSV files, validates it against a schema, and writes it back to disk.

    Args:
        input_dir (str): Path to the directory containing the OMOP dataset (CSV files).
        output_dir (str): Path to the directory where processed files will be saved.
        schema (dict): A dictionary defining the desired schema (column name -> data type).

    Returns:
        None
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Recursively find all CSV files in the input directory
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                print(f"Processing file: {file_path}")

                # Read the CSV file into a Polars DataFrame
                df = pl.read_csv(file_path)

                # Validate and convert the DataFrame to match the schema
                for column, dtype in schema.items():
                    if column not in df.columns:
                        # Add missing columns with default None values
                        df = df.with_columns(pl.lit(None, dtype=dtype).alias(column))
                    else:
                        # Cast existing columns to the correct type
                        df = df.with_columns(pl.col(column).cast(dtype))

                # Select only the columns in the schema
                df = df.select(list(schema.keys()))

                # Write the processed DataFrame to the output directory
                output_file_path = os.path.join(output_dir, os.path.relpath(file_path, input_dir))
                os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
                df.write_csv(output_file_path)
                print(f"Written to: {output_file_path}")
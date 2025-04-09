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


def convert_to_schema_polars(dataset, target_schema, allow_extra_columns=False):
    """
    Convert a Polars DataFrame or LazyFrame to match the target schema.

    Args:
        dataset (pl.DataFrame or pl.LazyFrame): The input dataset with a potentially different schema.
        target_schema (dict): A dictionary defining the desired schema (column name -> data type).
        allow_extra_columns (bool): If True, extra columns in the dataset are retained.

    Returns:
        pl.DataFrame or pl.LazyFrame: The dataset converted to match the target schema.
    """
    # Ensure the dataset is either a DataFrame or LazyFrame
    if not isinstance(dataset, (pl.DataFrame, pl.LazyFrame)):
        raise TypeError("Dataset must be a Polars DataFrame or LazyFrame.")

    # Add missing columns with default values
    for column, dtype in target_schema.items():
        if column not in dataset.columns:
            default_value = pl.lit(None, dtype=dtype).alias(column)
            dataset = dataset.with_columns(default_value)

    # If extra columns are not allowed, select only the target schema columns
    if not allow_extra_columns:
        dataset = dataset.select(list(target_schema.keys()))

    # Ensure column types match the target schema
    source_schema = dataset.collect_schema()

    for column, dtype in target_schema.items():
        if source_schema.get(column) != dtype:
            dataset = dataset.with_columns(pl.col(column).cast(dtype))

    return dataset

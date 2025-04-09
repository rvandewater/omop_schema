from pathlib import Path

import pyarrow as pa
from pyarrow import csv
from pyarrow import parquet as pq

from .convert import convert_to_schema_polars
from .schema.base import OMOPSchemaBase
from .schema.v5_3 import OMOPSchemaV53
from .schema.v5_4 import OMOPSchemaV54

try:
    import polars as pl

    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False
try:
    pass

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def get_schema_loader(omop_version):
    """
    Returns the appropriate schema loader based on the OMOP version.
    """
    if omop_version == "5.3" or omop_version == 5.3:
        return OMOPSchemaV53()
    elif omop_version == "5.4" or omop_version == 5.4:
        return OMOPSchemaV54()
    else:
        raise ValueError(f"Unsupported OMOP version: {omop_version}")


def pyarrow_to_polars_schema(arrow_schema: pa.Schema) -> dict:
    """
    Convert a PyArrow schema to a Polars schema.

    Args:
        arrow_schema (pa.Schema): The PyArrow schema to convert.

    Returns:
        dict: A dictionary representing the Polars schema.

    Raises:
        ImportError: If Polars is not installed.
        ValueError: If the PyArrow type is not supported.
    """
    if not POLARS_AVAILABLE:
        raise ImportError("Polars is not installed. Install it to use this function.")

    arrow_to_polars_map = {
        pa.int8(): pl.Int8,
        pa.int16(): pl.Int16,
        pa.int32(): pl.Int32,
        pa.int64(): pl.Int64,
        pa.uint8(): pl.UInt8,
        pa.uint16(): pl.UInt16,
        pa.uint32(): pl.UInt32,
        pa.uint64(): pl.UInt64,
        pa.float32(): pl.Float32,
        pa.float64(): pl.Float64,
        pa.string(): pl.Utf8,
        pa.binary(): pl.Binary,
        pa.bool_(): pl.Boolean,
        pa.date32(): pl.Date,
        pa.date64(): pl.Date,
        pa.timestamp("us"): pl.Datetime("us"),
        pa.timestamp("ns"): pl.Datetime("ns"),
    }

    polars_schema = {}
    for field in arrow_schema:
        arrow_type = field.type
        polars_type = arrow_to_polars_map.get(arrow_type, None)
        if polars_type is None:
            raise ValueError(f"Unsupported PyArrow type: {arrow_type}")
        polars_schema[field.name] = polars_type

    return polars_schema


def pyarrow_to_pandas_schema(arrow_schema: pa.Schema) -> dict:
    """
    Convert a PyArrow schema to a Pandas schema.

    Args:
        arrow_schema (pa.Schema): The PyArrow schema to convert.

    Returns:
        dict: A dictionary representing the Pandas schema.
    """
    arrow_to_pandas_map = {
        pa.int8(): "int8",
        pa.int16(): "int16",
        pa.int32(): "int32",
        pa.int64(): "int64",
        pa.uint8(): "uint8",
        pa.uint16(): "uint16",
        pa.uint32(): "uint32",
        pa.uint64(): "uint64",
        pa.float32(): "float32",
        pa.float64(): "float64",
        pa.string(): "object",
        pa.binary(): "object",
        pa.bool_(): "bool",
        pa.date32(): "datetime64[ns]",
        pa.date64(): "datetime64[ns]",
        pa.timestamp("us"): "timestamp[us]",
        pa.timestamp("ns"): "timestamp[ns]",
    }

    pandas_schema = {}
    for field in arrow_schema:
        arrow_type = field.type
        pandas_type = arrow_to_pandas_map.get(arrow_type, None)
        if pandas_type is None:
            raise ValueError(f"Unsupported PyArrow type: {arrow_type}")
        pandas_schema[field.name] = pandas_type

    return pandas_schema


def load_table(fp: str | Path, schema: OMOPSchemaBase = None) -> pa.Table | None:
    """
    Load a dataset for the given OMOP table using PyArrow.

    Args:
        fp (Path): Path to the file or directory.
        schema (OMOPSchemaBase, optional): Schema to validate and cast the table against.

    Returns:
        pa.Table | None: The loaded PyArrow Table, or None if no valid files are found.
    """
    if not isinstance(fp, Path):
        fp = Path(fp)
    table_name = fp.stem.split(".")[0]  # Infer table name from file path
    if fp.is_file():
        if fp.suffixes == [".csv", ".gz"] or fp.suffix == ".csv":
            table = csv.read_csv(fp, read_options=csv.ReadOptions(use_threads=True))
        elif fp.suffix == ".parquet":
            table = pq.read_table(fp)
        else:
            return None
    elif fp.is_dir():
        # Handle directory containing multiple files
        files = list(fp.glob("**/*"))
        csv_files = [file for file in files if file.suffix in [".csv", ".gz"]]
        parquet_files = [file for file in files if file.suffix == ".parquet"]

        if csv_files:
            tables = [
                csv.read_csv(file, read_options=csv.ReadOptions(use_threads=True)) for file in csv_files
            ]
            table = pa.concat_tables(tables)
        elif parquet_files:
            tables = [pq.read_table(file) for file in parquet_files]
            table = pa.concat_tables(tables)
        else:
            return None
    else:
        return None

    # If a schema is provided, validate and cast the table. Keep the extra columns.
    if schema:
        expected_schema = schema.get_pyarrow_schema(table_name)
        # Identify extra columns
        extra_columns = [
            (col, table.schema.field(col).type)
            for col in table.column_names
            if col not in [field.name for field in expected_schema]
        ]
        # Get the intersection of schema fields and table columns
        common_fields = [field for field in expected_schema if field.name in table.column_names]
        # Reorder table columns to match the common schema's field order
        reordered_columns = [field.name for field in common_fields] + [col for col, _ in extra_columns]
        table = table.select(reordered_columns)
        # Cast only the common columns
        casted_table = table.select([field.name for field in common_fields]).cast(pa.schema(common_fields))
        # Combine casted common columns with extra columns
        for col in extra_columns:
            casted_table = casted_table.append_column(col[0], table[col[0]])

        table = casted_table

    return table


def load_table_polars(fp: str | Path, schema: OMOPSchemaBase = None) -> pl.LazyFrame | None:
    """
    Load a dataset for the given OMOP table using Polars with lazy evaluation.

    Args:
        fp (Path): Path to the file or directory.
        schema (OMOPSchemaBase, optional): Schema to validate and cast the table against.

    Returns:
        pl.LazyFrame | None: The loaded Polars LazyFrame, or None if no valid files are found.
    """
    if not isinstance(fp, Path):
        fp = Path(fp)
    table_name = fp.stem.split(".")[0]  # Infer table name from file path

    if fp.is_file():
        if fp.suffix in [".csv", ".gz"]:
            table = pl.scan_csv(fp)
        elif fp.suffix == ".parquet":
            table = pl.scan_parquet(fp)
        else:
            return None
    elif fp.is_dir():
        # Handle directory containing multiple files
        files = list(fp.glob("**/*"))
        csv_files = [file for file in files if file.suffix in [".csv", ".gz"]]
        parquet_files = [file for file in files if file.suffix == ".parquet"]

        if csv_files:
            table = pl.scan(fp)
        elif parquet_files:
            table = pl.scan_parquet(fp)
        else:
            return None
    else:
        return None

    # If a schema is provided, validate and cast the table. Keep the extra columns.
    if schema:
        expected_schema = schema.get_schema(table_name)
        expected_schema = pyarrow_to_polars_schema(pa.schema(expected_schema))
        table = convert_to_schema_polars(table, expected_schema, allow_extra_columns=True)

    return table


def get_table_path(input_dir: str, table_name: str) -> Path | None:
    input_dir = Path(input_dir)
    table_path = input_dir / table_name
    if table_path.exists():
        return table_path
    table_path_with_ext = list(input_dir.glob(f"{table_name}.*"))
    if table_path_with_ext:
        return table_path_with_ext[0]
    return None

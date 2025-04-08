import pyarrow as pa

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
        pa.timestamp("us"): "datetime64[ns]",
        pa.timestamp("ns"): "datetime64[ns]",
    }

    pandas_schema = {}
    for field in arrow_schema:
        arrow_type = field.type
        pandas_type = arrow_to_pandas_map.get(arrow_type, None)
        if pandas_type is None:
            raise ValueError(f"Unsupported PyArrow type: {arrow_type}")
        pandas_schema[field.name] = pandas_type

    return pandas_schema

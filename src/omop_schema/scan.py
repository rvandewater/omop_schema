"""
Lazily read an OMOP table into its OMOP schema with Polars.

A table may be a `.csv`, `.csv.gz` or `.parquet` file, or a directory of such shards, as large OMOP exports
are often split. Column names are lowercased before the schema is applied, so uppercase headers get their
types too. Columns outside the schema, such as site extension columns, are kept unless asked otherwise, and
DATE columns exported as midnight timestamps ("2005-05-07 00:00:00", as SQL Server and Postgres dumps write
them) are read as dates.
"""

import csv
import gzip
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

import polars as pl

from .schema.base import OMOPSchemaBase

# A DATE written with a midnight time ("2005-05-07 00:00:00", "2005-05-07T00:00:00.000"). Any other time of
# day is left in place, so parsing it as a date fails loudly instead of dropping the time.
MIDNIGHT_TIME_SUFFIX = r"[ T]00:00:00(\.0+)?$"
# Text formats parsed into dates and datetimes, tried in order: ISO first, then the year-first and day-first
# forms Polars infers (a day-first "07-05-2005" is 7 May), and compact dates.
DATE_FORMATS = ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y", "%Y%m%d")
DATETIME_FORMATS = (
    "%Y-%m-%d %H:%M:%S%.f",
    "%Y-%m-%dT%H:%M:%S%.f",
    "%Y-%m-%d %H:%M",
    "%Y/%m/%d %H:%M:%S%.f",
    "%d-%m-%Y %H:%M:%S%.f",
    "%d/%m/%Y %H:%M:%S%.f",
    "%Y-%m-%d",
)
# Shards concatenated per step; one concat over thousands of lazy shards can exhaust memory in Polars.
SHARDS_PER_CONCAT = 64

PolarsSchema = Mapping[str, pl.DataType]


def table_name_from_path(path: str | Path) -> str:
    """
    Return the OMOP table a file or directory holds: its name up to the first dot.

    Examples:
        >>> table_name_from_path("omop/measurement.csv.gz"), table_name_from_path("omop/measurement")
        ('measurement', 'measurement')
    """
    return Path(path).name.split(".")[0]


def _parse_text(
    text: pl.Expr, formats: Sequence[str], parse: Callable[[pl.Expr, str, bool], pl.Expr], strict: bool
) -> pl.Expr:
    parsed = pl.coalesce([parse(text, fmt, False) for fmt in formats])
    if not strict:
        return parsed
    # Text that matches no format is parsed once more, strictly, so the error names the offending values.
    return pl.coalesce(parsed, parse(pl.when(parsed.is_null()).then(text), formats[0], True))


def cast_to_type(column: str, source: pl.DataType, target: pl.DataType, strict: bool = True) -> pl.Expr:
    """
    Return an expression casting `column` from type `source` to `target`.

    Text is parsed into dates (`DATE_FORMATS`, after dropping a midnight time) and datetimes
    (`DATETIME_FORMATS`), which Polars 2 no longer casts.

    Args:
        column: The column name.
        source: Its current type.
        target: The type to cast to.
        strict: If True, a value that cannot be cast raises when collected; if False, it becomes null.

    Examples:
        >>> df = pl.DataFrame({"d": ["2005-05-07", "2005-05-08 00:00:00", "20050509", None]})
        >>> df.select(cast_to_type("d", pl.String, pl.Date))["d"].to_list()
        [datetime.date(2005, 5, 7), datetime.date(2005, 5, 8), datetime.date(2005, 5, 9), None]
        >>> df = pl.DataFrame({"t": ["2005-05-07 08:30:00", "2005-05-07T09:00:00.5", "07/05/2005"]})
        >>> df.select(cast_to_type("t", pl.String, pl.Datetime("us"), strict=False))["t"].to_list()
        [datetime.datetime(2005, 5, 7, 8, 30), datetime.datetime(2005, 5, 7, 9, 0, 0, 500000), None]
    """
    col = pl.col(column)
    if source == target:
        return col
    if source == pl.String and target == pl.Date:
        text = col.str.replace(MIDNIGHT_TIME_SUFFIX, "")
        return _parse_text(text, DATE_FORMATS, lambda e, f, s: e.str.to_date(f, strict=s), strict).alias(
            column
        )
    if source == pl.String and isinstance(target, pl.Datetime):

        def parse(expr: pl.Expr, fmt: str, strict_: bool) -> pl.Expr:
            return expr.str.to_datetime(
                fmt, strict=strict_, time_unit=target.time_unit, time_zone=target.time_zone
            )

        return _parse_text(col, DATETIME_FORMATS, parse, strict).alias(column)
    return col.cast(target, strict=strict)


def scan_table(
    source: str | Path | Sequence[str | Path],
    schema: OMOPSchemaBase | PolarsSchema | None = None,
    table_name: str | None = None,
    *,
    selector=None,
    strict: bool = True,
    keep_extra_columns: bool = True,
    add_missing_columns: bool = False,
    lowercase_columns: bool = True,
) -> pl.LazyFrame | None:
    """
    Lazily read an OMOP table in its OMOP schema.

    Every file is read on its own and the files are then stacked by column name, so shards may order their
    columns differently, lack a column, or carry one the others do not; a column a shard lacks is null there.

    Args:
        source: A `.csv`, `.csv.gz` or `.parquet` file, a directory of such shards (searched recursively),
            or a list of shard files. A directory holding both CSV and Parquet shards is read from its CSV
            shards.
        schema: An OMOP schema (or any object with `get_polars_schema` or `get_pyarrow_schema`), whose
            `table_name` table is applied; a mapping of column names to Polars types; or None to keep the
            types as read.
        table_name: The OMOP table; inferred from `source` when it is a single path.
        selector: Polars selector or column names to keep, applied last, to the lowercased columns.
        strict: If True, a value that does not fit its schema type raises when collected. If False, it
            becomes null: a relaxed alignment for exports whose types drift between shards.
        keep_extra_columns: If True, columns outside the schema (such as site extension columns) are kept
            with the type they were read with; if False, only schema columns are kept.
        add_missing_columns: If True, schema columns the input lacks are added as nulls.
        lowercase_columns: If True, column names are lowercased. Schema columns are matched regardless of
            case either way.

    Returns:
        The table, or None if `source` does not exist or holds no CSV or Parquet file.

    Raises:
        ValueError: If `source` is a list of files, `schema` is an OMOP schema and `table_name` is not given.

    Examples:
        >>> import tempfile
        >>> from omop_schema.versions import get_schema_loader
        >>> with tempfile.TemporaryDirectory() as d:
        ...     fp = Path(d) / "death.csv"
        ...     _ = fp.write_text("PERSON_ID,DEATH_DATE,xtn_cause\\n1,2005-05-07 00:00:00,unknown\\n")
        ...     scan_table(fp, get_schema_loader("5.4")).collect()
        shape: (1, 3)
        ┌───────────┬────────────┬───────────┐
        │ person_id ┆ death_date ┆ xtn_cause │
        │ ---       ┆ ---        ┆ ---       │
        │ i64       ┆ date       ┆ str       │
        ╞═══════════╪════════════╪═══════════╡
        │ 1         ┆ 2005-05-07 ┆ unknown   │
        └───────────┴────────────┴───────────┘
    """
    if isinstance(source, (str, Path)):
        path = Path(source)
        files = sorted(p for p in path.glob("**/*") if p.is_file()) if path.is_dir() else [path]
        files = [fp for fp in files if fp.is_file()]
        table_name = table_name or table_name_from_path(path)
    else:
        files = [Path(p) for p in source]
        if table_name is None and schema is not None and not isinstance(schema, Mapping):
            raise ValueError("Pass `table_name` to scan a list of files with an OMOP schema.")
    target = _table_schema(schema, table_name)

    csv_files = [fp for fp in files if fp.name.lower().endswith((".csv", ".csv.gz"))]
    parquet_files = [fp for fp in files if fp.name.lower().endswith(".parquet")]
    if csv_files:
        frames = [_scan_csv_file(fp, target, strict, lowercase_columns) for fp in csv_files]
    elif parquet_files:
        frames = [_scan_parquet_file(fp, target, strict, lowercase_columns) for fp in parquet_files]
    else:
        return None

    table = _stack(frames)
    present = table.collect_schema().names()
    if add_missing_columns:
        table = table.with_columns(
            pl.lit(None, dtype=dtype).alias(name) for name, dtype in target.items() if name not in present
        )
    if not keep_extra_columns:
        table = table.select(name for name in table.collect_schema().names() if name.lower() in target)
    if selector is not None:
        table = table.select(selector)
    return table


def _table_schema(schema, table_name: str | None) -> dict[str, pl.DataType]:
    """The Polars types of `table_name` from an OMOP schema (or any object like one), or of a mapping."""
    if schema is None or isinstance(schema, Mapping):
        return dict(schema or {})
    if hasattr(schema, "get_polars_schema"):
        return dict(schema.get_polars_schema(table_name))
    from .utils import pyarrow_to_polars_schema

    return pyarrow_to_polars_schema(schema.get_pyarrow_schema(table_name))


def _csv_header(fp: Path) -> list[str]:
    """The column names in the first line of a CSV or gzipped CSV file, without reading the rest."""
    opener = gzip.open if fp.name.lower().endswith(".gz") else open
    with opener(fp, "rt", encoding="utf-8-sig", newline="") as f:
        return next(csv.reader(f), [])


def _renamed(names: list[str], lowercase: bool) -> dict[str, str]:
    return {name: name.lower() for name in names if lowercase and name != name.lower()}


def _scan_csv_file(fp: Path, target: PolarsSchema, strict: bool, lowercase: bool) -> pl.LazyFrame:
    header = _csv_header(fp)
    renamed = _renamed(header, lowercase)
    # The CSV reader parses the schema types itself, except dates: they are read as text, so a midnight time
    # can be dropped before parsing. Columns outside the schema stay text.
    read_as = {name: target[name.lower()] for name in header if name.lower() in target}
    read_as = {name: pl.String if dtype == pl.Date else dtype for name, dtype in read_as.items()}
    frame = pl.scan_csv(fp, infer_schema_length=0, schema_overrides=read_as, ignore_errors=not strict)
    return frame.rename(renamed).with_columns(
        cast_to_type(renamed.get(name, name), pl.String, pl.Date, strict)
        for name in header
        if target.get(name.lower()) == pl.Date
    )


def _scan_parquet_file(fp: Path, target: PolarsSchema, strict: bool, lowercase: bool) -> pl.LazyFrame:
    frame = pl.scan_parquet(fp)
    current = frame.collect_schema()
    renamed = _renamed(current.names(), lowercase)
    return frame.rename(renamed).with_columns(
        cast_to_type(renamed.get(name, name), dtype, target[name.lower()], strict)
        for name, dtype in current.items()
        if name.lower() in target and dtype != target[name.lower()]
    )


def _stack(frames: list[pl.LazyFrame]) -> pl.LazyFrame:
    """Stack shards by column name, filling a column a shard lacks with nulls."""
    while len(frames) > 1:
        frames = [
            pl.concat(frames[i : i + SHARDS_PER_CONCAT], how="diagonal_relaxed")
            for i in range(0, len(frames), SHARDS_PER_CONCAT)
        ]
    return frames[0]

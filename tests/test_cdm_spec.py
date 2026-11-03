"""Every schema against the official OMOP CDM field lists in `tests/cdm_spec/`."""

import csv
from pathlib import Path

import pyarrow as pa
import pytest

from omop_schema.versions import SUPPORTED_VERSIONS, get_schema_loader

SPEC_DIR = Path(__file__).parent / "cdm_spec"
# CDM datatype -> Arrow type; every varchar(n) is a string.
ARROW_TYPES = {
    "integer": pa.int64(),
    "float": pa.float64(),
    "date": pa.date64(),
    "datetime": pa.timestamp("us"),
}


def _spec(version: str) -> dict[str, dict[str, str]]:
    fields: dict[str, dict[str, str]] = {}
    with open(SPEC_DIR / f"cdm_v{version}_fields.csv", newline="") as f:
        for row in csv.DictReader(f):
            fields.setdefault(row["table"], {})[row["field"]] = row["datatype"]
    return fields


@pytest.mark.parametrize("version", SUPPORTED_VERSIONS)
def test_schema_has_exactly_the_cdm_tables_and_fields(version):
    spec, schema = _spec(version), get_schema_loader(version)

    assert sorted(schema.get_table_names()) == sorted(spec)
    assert {t: sorted(schema.get_schema(t)) for t in spec} == {
        t: sorted(fields) for t, fields in spec.items()
    }


@pytest.mark.parametrize("version", SUPPORTED_VERSIONS)
def test_schema_types_follow_the_cdm_datatypes(version):
    spec, schema = _spec(version), get_schema_loader(version)

    mismatched = {
        f"{table}.{field}": (cdm_type, str(schema.get_schema(table)[field]))
        for table, fields in spec.items()
        for field, cdm_type in fields.items()
        if schema.get_schema(table)[field] != ARROW_TYPES.get(cdm_type, pa.string())
    }
    assert mismatched == {}


@pytest.mark.parametrize(("older", "newer"), [("5.3", "5.4"), ("5.4", "5.5")])
def test_fields_a_version_keeps_keep_their_type(older, newer):
    old, new = get_schema_loader(older), get_schema_loader(newer)
    changed = {
        f"{table}.{field}": (str(dtype), str(new.get_schema(table)[field]))
        for table in set(old.get_table_names()) & set(new.get_table_names())
        for field, dtype in old.get_schema(table).items()
        if field in new.get_schema(table) and new.get_schema(table)[field] != dtype
    }
    assert changed == {}

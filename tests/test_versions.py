"""Picking a schema by OMOP CDM version."""

import pytest

from omop_schema.schema.v5_3 import OMOPSchemaV53
from omop_schema.schema.v5_4 import OMOPSchemaV54
from omop_schema.schema.v5_5 import OMOPSchemaV55
from omop_schema.utils import get_schema_loader as utils_get_schema_loader
from omop_schema.versions import (
    SUPPORTED_VERSIONS,
    get_schema_loader,
    normalize_omop_version,
)


@pytest.mark.parametrize(
    ("given", "expected"),
    [(5.3, "5.3"), ("5.4", "5.4"), ("v5.4.2", "5.4"), ("V5.5.0", "5.5"), (" 5.5 ", "5.5"), (5.50, "5.5")],
)
def test_normalize_omop_version(given, expected):
    assert normalize_omop_version(given) == expected


@pytest.mark.parametrize("given", ["5.2", "6.0", "5", "five", "", None])
def test_unsupported_versions_are_rejected(given):
    with pytest.raises(ValueError, match="supported versions: 5.3, 5.4, 5.5"):
        normalize_omop_version(given)


@pytest.mark.parametrize(
    ("version", "schema_class"), [(5.3, OMOPSchemaV53), ("5.4", OMOPSchemaV54), ("v5.5.0", OMOPSchemaV55)]
)
def test_get_schema_loader(version, schema_class):
    for loader in (get_schema_loader, utils_get_schema_loader):
        schema = loader(version)
        assert type(schema) is schema_class
        assert schema.version == normalize_omop_version(version)


def test_supported_versions_are_ordered_and_each_has_a_schema():
    assert SUPPORTED_VERSIONS == ("5.3", "5.4", "5.5")
    assert [get_schema_loader(v).version for v in SUPPORTED_VERSIONS] == list(SUPPORTED_VERSIONS)


def test_unsupported_version_from_utils_still_raises_value_error():
    with pytest.raises(ValueError):
        utils_get_schema_loader("4.0")

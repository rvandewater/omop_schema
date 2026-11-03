"""The OMOP CDM versions this package has a schema for, and how to pick one by name."""

import re

from .schema.base import OMOPSchemaBase
from .schema.v5_3 import OMOPSchemaV53
from .schema.v5_4 import OMOPSchemaV54
from .schema.v5_5 import OMOPSchemaV55

#: Schema class per supported OMOP CDM version.
SCHEMAS: dict[str, type[OMOPSchemaBase]] = {
    schema.version: schema for schema in (OMOPSchemaV53, OMOPSchemaV54, OMOPSchemaV55)
}
SUPPORTED_VERSIONS: tuple[str, ...] = tuple(SCHEMAS)

_VERSION_PATTERN = re.compile(r"v?(\d+)\.(\d+)(?:\.\d+)?", re.IGNORECASE)


def normalize_omop_version(version: str | float) -> str:
    """
    Return the supported OMOP CDM version `version` names, as "<major>.<minor>".

    Patch releases (such as CDM v5.4.2) have the tables and fields of their minor version.

    Raises:
        ValueError: If `version` is not a supported OMOP CDM version.

    Examples:
        >>> normalize_omop_version(5.4), normalize_omop_version("v5.4.2"), normalize_omop_version(" 5.5 ")
        ('5.4', '5.4', '5.5')
        >>> normalize_omop_version("6.0")
        Traceback (most recent call last):
        ...
        ValueError: Unsupported OMOP CDM version '6.0'; supported versions: 5.3, 5.4, 5.5.
    """
    match = _VERSION_PATTERN.fullmatch(str(version).strip())
    normalized = f"{match[1]}.{match[2]}" if match else None
    if normalized not in SCHEMAS:
        raise ValueError(
            f"Unsupported OMOP CDM version {str(version)!r}; "
            f"supported versions: {', '.join(SUPPORTED_VERSIONS)}."
        )
    return normalized


def get_schema_loader(version: str | float) -> OMOPSchemaBase:
    """
    Return the schema of an OMOP CDM version.

    Args:
        version: The version, e.g. 5.4, "5.4" or "v5.4.2".

    Raises:
        ValueError: If `version` is not a supported OMOP CDM version.

    Examples:
        >>> schema = get_schema_loader("5.5")
        >>> type(schema).__name__, schema.version
        ('OMOPSchemaV55', '5.5')
    """
    return SCHEMAS[normalize_omop_version(version)]()

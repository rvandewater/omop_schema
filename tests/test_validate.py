import pytest
import pyarrow as pa
from src.omop_schema.validate import OMOPValidator
from src.omop_schema.schema.v5_3 import OMOPSchemaV53

@pytest.fixture
def validator():
    """Fixture to initialize the OMOPValidator with the OMOPSchemaV5."""
    return OMOPValidator(OMOPSchemaV53)

@pytest.fixture
def valid_table():
    """Fixture to create a valid dataset for the 'person' table."""
    schema = pa.schema([
        ("person_id", pa.int64()),
        ("gender_concept_id", pa.int64()),
        ("year_of_birth", pa.int64()),
        ("month_of_birth", pa.int64()),
        ("day_of_birth", pa.int64()),
        ("birth_datetime", pa.timestamp("us")),  # Add this column
        ("race_concept_id", pa.int64()),
        ("ethnicity_concept_id", pa.int64()),
        ("location_id", pa.int64()),
        ("provider_id", pa.int64()),
        ("care_site_id", pa.int64()),
        ("person_source_value", pa.string()),
        ("gender_source_value", pa.string()),
        ("gender_source_concept_id", pa.int64()),
        ("race_source_value", pa.string()),
        ("race_source_concept_id", pa.int64()),
        ("ethnicity_source_value", pa.string()),
        ("ethnicity_source_concept_id", pa.int64()),
    ])
    return pa.Table.from_arrays([pa.array([]) for _ in schema], schema=schema)

@pytest.fixture
def invalid_table(valid_table):
    """Fixture to create an invalid dataset by removing specific columns."""
    valid_schema = valid_table.schema
    # Remove 'month_of_birth' and 'day_of_birth' columns
    invalid_schema = pa.schema(
        [field for field in valid_schema if field.name not in {"month_of_birth", "day_of_birth"}]
    )
    return pa.Table.from_arrays([valid_table[column.name] for column in invalid_schema], schema=invalid_schema)

@pytest.fixture
def valid_table_extended(valid_table):
    """Fixture to create a valid extended dataset by adding an extra column."""
    valid_schema = valid_table.schema
    # Add an extra column to the schema
    extended_schema = valid_schema.append(pa.field("extra_column_1", pa.string()))
    # Create the extended table with the extra column
    extended_arrays = [valid_table[column.name] for column in valid_schema] + [pa.array([])]
    return pa.Table.from_arrays(extended_arrays, schema=extended_schema)

def test_valid_dataset(validator, valid_table):
    """Test that a valid dataset passes validation."""
    result = validator.validate_table("person", valid_table)
    assert not result["missing_columns"], f"Unexpected missing columns: {result['missing_columns']}"
    assert not result["mismatched_columns"], f"Unexpected mismatched columns: {result['mismatched_columns']}"

def test_invalid_dataset(validator, invalid_table):
    """Test that an invalid dataset fails validation."""
    result = validator.validate_table("person", invalid_table)
    assert "month_of_birth" in result["missing_columns"], "Expected 'month_of_birth' to be missing."
    assert "day_of_birth" in result["missing_columns"], "Expected 'day_of_birth' to be missing."
    assert not result["mismatched_columns"], f"Unexpected mismatched columns: {result['mismatched_columns']}"

def test_valid_dataset_extended(validator, valid_table_extended):
    """Test that a valid dataset with extra columns passes validation."""
    result = validator.validate_table("person", valid_table_extended)
    assert not result["missing_columns"], f"Unexpected missing columns: {result['missing_columns']}"
    assert not result["mismatched_columns"], f"Unexpected mismatched columns: {result['mismatched_columns']}"
    assert result["extra_columns"] == ["extra_column_1"], f"Unexpected extra columns: {result['extra_columns']}"
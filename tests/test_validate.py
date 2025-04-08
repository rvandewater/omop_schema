import pytest
import pyarrow as pa
from src.omop_schema.validate import OMOPValidator
from src.omop_schema.schema.v5_3 import OMOPSchemaV53

@pytest.fixture
def validator():
    """Fixture to initialize the OMOPValidator with the OMOPSchemaV5."""
    return OMOPValidator(OMOPSchemaV53)

@pytest.fixture
def valid_dataset():
    """Fixture to create a valid dataset for the 'person' table."""
    schema = pa.schema([
        ("person_id", pa.int64()),
        ("gender_concept_id", pa.int64()),
        ("year_of_birth", pa.int64()),
        ("month_of_birth", pa.int64()),
        ("day_of_birth", pa.int64()),
        ("birth_datetime", pa.timestamp("us")),  # Add this column
        ("time_of_birth", pa.string()),
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
def invalid_dataset():
    """Fixture to create an invalid dataset for the 'person' table."""
    schema = pa.schema([
        ("person_id", pa.int64()),
        ("gender_concept_id", pa.int64()),
        ("year_of_birth", pa.int64()),
        # Missing 'month_of_birth' and 'day_of_birth'
        ("time_of_birth", pa.string()),
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

def test_valid_dataset(validator, valid_dataset):
    """Test that a valid dataset passes validation."""
    result = validator.validate_table("person", valid_dataset)
    assert not result["missing_columns"], f"Unexpected missing columns: {result['missing_columns']}"
    assert not result["mismatched_columns"], f"Unexpected mismatched columns: {result['mismatched_columns']}"

def test_invalid_dataset(validator, invalid_dataset):
    """Test that an invalid dataset fails validation."""
    result = validator.validate_table("person", invalid_dataset)
    assert "month_of_birth" in result["missing_columns"], "Expected 'month_of_birth' to be missing."
    assert "day_of_birth" in result["missing_columns"], "Expected 'day_of_birth' to be missing."
    assert not result["mismatched_columns"], f"Unexpected mismatched columns: {result['mismatched_columns']}"
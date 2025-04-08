import pyarrow as pa
import pytest
from src.omop_schema.convert import convert_to_schema

def test_convert_to_schema():
    """Test the convert_to_schema function."""
    # Define the target schema
    target_schema = pa.schema([
        pa.field("person_id", pa.int64()),
        pa.field("gender_concept_id", pa.int64()),
        pa.field("year_of_birth", pa.int64()),
    ])

    # Create a mock dataset with a different schema
    dataset = pa.table({
        "person_id": [1, 2],
        "gender_concept_id": [3, 4],
        "extra_column": ["extra1", "extra2"],  # Extra column not in target schema
    })

    # Convert the dataset to match the target schema
    converted_dataset = convert_to_schema(dataset, target_schema)

    # Validate the converted dataset
    assert converted_dataset.schema == target_schema, "Schema mismatch after conversion."
    assert converted_dataset.num_rows == 2, "Row count mismatch after conversion."
    assert converted_dataset.column("person_id").to_pylist() == [1, 2], "Data mismatch in 'person_id' column."
    assert converted_dataset.column("gender_concept_id").to_pylist() == [3, 4], "Data mismatch in 'gender_concept_id' column."
    assert "year_of_birth" in converted_dataset.schema.names, "Missing column 'year_of_birth' after conversion."
    assert converted_dataset.column("year_of_birth").to_pylist() == [None, None], "Default values for 'year_of_birth' are incorrect."
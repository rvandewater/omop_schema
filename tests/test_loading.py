import pytest
import pyarrow as pa
import os
import tempfile
import pyarrow.csv as csv
from src.omop_schema.schema.base import OMOPSchemaBase

class MockOMOPSchema(OMOPSchemaBase):
    """Mock subclass of OMOPSchemaBase for testing."""
    def _load_schema(self):
        return {
            "person": {
                "person_id": pa.int64(),
                "gender_concept_id": pa.int64(),
                "year_of_birth": pa.int64(),
            }
        }

@pytest.fixture
def mock_csv_files():
    """Fixture to create temporary CSV files for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a mock CSV file for the 'person' table
        person_data = "person_id,gender_concept_id,year_of_birth\n1,2,1980\n3,4,1990"
        person_file = os.path.join(temp_dir, "person.csv")
        with open(person_file, "w") as f:
            f.write(person_data)
        yield temp_dir

def test_load_csv_dataset(mock_csv_files):
    """Test the load_csv_dataset method."""
    schema = MockOMOPSchema()
    datasets = schema.load_csv_dataset(mock_csv_files)

    # Validate the loaded dataset
    assert "person" in datasets, "Expected 'person' table to be loaded."
    table = datasets["person"]
    assert table.schema.names == ["person_id", "gender_concept_id", "year_of_birth"], "Schema mismatch."
    assert table.num_rows == 2, "Row count mismatch."
    assert table.column("person_id").to_pylist() == [1, 3], "Data mismatch in 'person_id' column."
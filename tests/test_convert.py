import polars as pl
import pyarrow as pa

from omop_schema.convert import convert_to_schema, convert_to_schema_polars


def test_convert_to_schema():
    """Test the convert_to_schema function."""
    # Define the target schema
    target_schema = pa.schema(
        [
            pa.field("person_id", pa.int64()),
            pa.field("gender_concept_id", pa.int64()),
            pa.field("year_of_birth", pa.int64()),
        ]
    )

    # Create a mock dataset with a different schema
    dataset = pa.table(
        {
            "person_id": [1, 2],
            "gender_concept_id": [3, 4],
            "extra_column": ["extra1", "extra2"],  # Extra column not in target schema
        }
    )

    # Convert the dataset to match the target schema
    converted_dataset = convert_to_schema(dataset, target_schema)

    # Validate the converted dataset
    assert converted_dataset.schema == target_schema, "Schema mismatch after conversion."
    assert converted_dataset.num_rows == 2, "Row count mismatch after conversion."
    assert converted_dataset.column("person_id").to_pylist() == [1, 2], "Data mismatch in 'person_id' column."
    assert converted_dataset.column("gender_concept_id").to_pylist() == [
        3,
        4,
    ], "Data mismatch in 'gender_concept_id' column."
    assert (
        "year_of_birth" in converted_dataset.schema.names
    ), "Missing column 'year_of_birth' after conversion."
    assert converted_dataset.column("year_of_birth").to_pylist() == [
        None,
        None,
    ], "Default values for 'year_of_birth' are incorrect."


def test_convert_to_schema_polars():
    """Test the convert_to_schema_polars function for Polars."""
    # Define the target schema
    target_schema = {
        "col1": pl.Int64,
        "col2": pl.Utf8,
        "col3": pl.Float64,
    }

    # Create a Polars DataFrame with a different schema
    source_schema = {
        "col1": pl.Int32,
        "col2": pl.Utf8,
        "extra_col": pl.Boolean,
    }

    data = pl.DataFrame(
        {
            "col1": [1, 2],
            "col2": ["a", "b"],
            "extra_col": [True, False],  # Extra column not in target schema
        },
        schema=source_schema,
    )

    # Test with DataFrame
    converted_df = convert_to_schema_polars(
        data, target_schema, allow_extra_columns=False, add_missing_columns=True
    )
    assert converted_df.schema == target_schema, "Schema mismatch for DataFrame."
    assert "col3" in converted_df.columns, "Missing column 'col3' in DataFrame."
    assert converted_df["col3"].to_list() == [None, None], "Default values for 'col3' are incorrect."

    # Test with LazyFrame
    lazy_data = data.lazy()
    converted_lf = convert_to_schema_polars(
        lazy_data, target_schema, allow_extra_columns=False, add_missing_columns=True
    )
    assert isinstance(converted_lf, pl.LazyFrame), "Result is not a LazyFrame."
    assert converted_lf.collect().schema == target_schema, "Schema mismatch for LazyFrame."
    assert "col3" in converted_lf.collect().columns, "Missing column 'col3' in LazyFrame."
    assert converted_lf.collect()["col3"].to_list() == [
        None,
        None,
    ], "Default values for 'col3' are incorrect."

    # Test with allow_extra_columns=True
    converted_df_extra = convert_to_schema_polars(data, target_schema, allow_extra_columns=True)
    assert "extra_col" in converted_df_extra.columns, "Extra column 'extra_col' was removed unexpectedly."

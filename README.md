# OMOP Schema

`omop_schema` is a Python package designed to read, manage, and convert OMOP (Observational Medical Outcomes Partnership) data into the correct schema. It provides tools to handle OMOP CDM (Common Data Model) tables, convert schemas between different formats (e.g., PyArrow, Polars, Pandas), and load datasets efficiently.

## Features

- **Schema Management**: Define and manage schemas for OMOP CDM tables for different versions (e.g., 5.3, v5.4).
- **Schema Conversion**: Convert PyArrow schemas to Polars or Pandas-compatible schemas.
- **Dataset Loading**: Load datasets from CSV files into PyArrow tables, ensuring they match the defined schema.
- **Optional Dependencies**: Support for Polars and Pandas as optional dependencies for schema conversion.

## Installation

Install the package using `pip`:

```bash
pip install omop_schema
```

To include optional dependencies:

```bash
pip install omop_schema[polars]
pip install omop_schema[pandas]
pip install omop_schema[polars,pandas]
```

## Usage

### 1. Define and Retrieve OMOP Schemas

The package provides predefined schemas for OMOP CDM tables. You can retrieve the schema for a specific table:

```python
from omop_schema.schema.v54 import OMOPSchemaV54

schema_v54 = OMOPSchemaV54()
concept_schema = schema_v54.get_pyarrow_schema("concept")
print(concept_schema)
```

### 2. Load Datasets

You can load datasets from a folder containing CSV files. The files are matched to the predefined schemas:

```python
from omop_schema.schema.v54 import OMOPSchemaV54

schema_v54 = OMOPSchemaV54()
datasets = schema_v54.load_csv_dataset("path/to/csv/folder")

# Access a specific table
concept_table = datasets["concept"]
print(concept_table)
```

### 3. Convert PyArrow Schema to Polars Schema

If Polars is installed, you can convert a PyArrow schema to a Polars-compatible schema:

```python
from omop_schema.utils import pyarrow_to_polars_schema
import pyarrow as pa

arrow_schema = pa.schema(
    [
        pa.field("column1", pa.int64()),
        pa.field("column2", pa.string()),
    ]
)

polars_schema = pyarrow_to_polars_schema(arrow_schema)
print(polars_schema)
```

### 4. Convert PyArrow Schema to Pandas Schema

If Pandas is installed, you can convert a PyArrow schema to a Pandas-compatible schema:

```python
from omop_schema.utils import pyarrow_to_pandas_schema
import pyarrow as pa

arrow_schema = pa.schema(
    [
        pa.field("column1", pa.int64()),
        pa.field("column2", pa.string()),
    ]
)

pandas_schema = pyarrow_to_pandas_schema(arrow_schema)
print(pandas_schema)
```

## Optional Dependencies

- **Polars**: For converting PyArrow schemas to Polars schemas.
- **Pandas**: For converting PyArrow schemas to Pandas schemas.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on the [GitHub repository](https://github.com/rvandewater/omop_schema).

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

```
```

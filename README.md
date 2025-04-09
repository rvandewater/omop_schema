# OMOP Schema

[![PyPI - Version](https://img.shields.io/pypi/v/omop_schema)](https://pypi.org/project/omop_schema/)
[![codecov](https://codecov.io/gh/rvandewater/omop_schema/graph/badge.svg?token=RW6JXHNT0W)](https://codecov.io/gh/rvandewater/omop_schema)
[![Tests](https://github.com/rvandewater/omop_schema/actions/workflows/tests.yaml/badge.svg)](https://github.com/rvandewater/omop_schema/actions/workflows/tests.yaml)
[![Code Quality](https://github.com/rvandewater/omop_schema/actions/workflows/code-quality-pr.yaml/badge.svg)](https://github.com/rvandewater/omop_schema/actions/workflows/code-quality-pr.yaml)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue?logo=python&logoColor=white)
[![License](https://img.shields.io/badge/License-MIT-green.svg?labelColor=gray)](https://github.com/rvandewater/omop_schema/blob/main/LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/rvandewater/omop_schema/pulls)
[![Contributors](https://img.shields.io/github/contributors/rvandewater/omop_schema.svg)](https://github.com/rvandewater/omop_schema/graphs/contributors)

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

# OMOP Dataset Validation - Graphical Method

This documentation provides an overview of how to use the `validate_omop_dataset_graphically` function to validate OMOP datasets and display the results in a graphical format.

The `validate_omop_dataset_graphically` function validates an OMOP dataset against a predefined schema and displays the results in a graphical table format using the `rich` library. It also logs the validation process for real-time feedback.

```python
validate_omop_dataset_graphically(validator, dataset_path="path/to/dataset")
```

The function will:
- Log the validation progress in real-time.
- Display a graphical table summarizing:
  - Missing columns
  - Mismatched columns
  - Extra columns
  - Correct columns

---

## **Example Output**

### **Console Log**
```plaintext
2023-10-01 12:00:00 - INFO - Validating table: person
2023-10-01 12:00:01 - INFO - Validation results for table 'person': Missing: month_of_birth, Mismatched: None, Extra: extra_column_1, Correct: person_id, gender_concept_id
2023-10-01 12:00:01 - INFO - Validation process completed.
```

### **Graphical Table**
```
+-------------+-----------------------------+-----------------------------------+----------------------+----------------------+
| Table Name  | Missing Columns             | Mismatched Columns               | Extra Columns        | Correct Columns      |
+-------------+-----------------------------+-----------------------------------+----------------------+----------------------+
| person      | month_of_birth: int64       | None                              | extra_column_1: str  | person_id: int64     |
|             | day_of_birth: int64         |                                   |                      | gender_concept_id:   |
|             |                             |                                   |                      | int64                |
+-------------+-----------------------------+-----------------------------------+----------------------+----------------------+
```

---

## **Parameters**

| Parameter                | Type            | Description                                                                 |
|--------------------------|-----------------|-----------------------------------------------------------------------------|
| `validator`              | `OMOPValidator`| The validator object containing the schema for validation.                 |
| `dataset_path`           | `str | Path`   | Path to the dataset directory or file to validate.                         |
| `load_with_expected_schema` | `bool`      | Whether to load the dataset with the expected schema. Default is `True`.   |

---

## **Notes**
- Ensure the dataset files are in a supported format (e.g., `.csv`, `.parquet`).
- The function uses the `rich` library for graphical output and `logging` for real-time feedback.
- Missing or mismatched columns are highlighted in the output for easy identification.

---

## **Troubleshooting**
- **Missing Dependencies**: Install the required libraries using `pip install rich`.
- **Invalid Dataset Path**: Ensure the dataset path is correct and accessible.
- **Schema Issues**: Verify the schema file is correctly defined and matches the dataset structure.
## Contributing

Contributions are welcome! Please open an issue or submit a pull request on the [GitHub repository](https://github.com/rvandewater/omop_schema).

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

```
```

# Welcome to the `omop_schema` Documentation

The `omop_schema` package provides tools for working with OMOP Common Data Model (CDM) schemas, including schema validation, dataset loading, and schema conversion for Python libraries like PyArrow, Polars, and Pandas.

---

## **Features**

- **Schema Validation**: Validate datasets against predefined OMOP CDM schemas.
- **Graphical Validation**: Display validation results in a graphical table format using the `rich` library.
- **Schema Conversion**: Convert PyArrow schemas to Polars or Pandas-compatible schemas.
- **Dataset Loading**: Load datasets from CSV files into PyArrow tables, ensuring they match the defined schema.
- **Optional Dependencies**: Support for Polars and Pandas as optional dependencies for schema conversion.

---

## **Installation**

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

---

## **Getting Started**

### **1. Define and Retrieve OMOP Schemas**

Retrieve predefined schemas for OMOP CDM tables:

```python
from omop_schema.schema.v54 import OMOPSchemaV54

schema_v54 = OMOPSchemaV54()
concept_schema = schema_v54.get_pyarrow_schema("concept")
print(concept_schema)
```

### **2. Validate Datasets Graphically**

Validate datasets and display results in a graphical table format:

```python
from omop_schema.validate import OMOPValidator, validate_omop_dataset_graphically
from omop_schema.schema.v54 import OMOPSchemaV54

validator = OMOPValidator(schema=OMOPSchemaV54())
validate_omop_dataset_graphically(validator, dataset_path="path/to/dataset")
```

### **3. Convert Schemas**

Convert PyArrow schemas to Polars or Pandas-compatible schemas:

```python
from omop_schema.utils import pyarrow_to_polars_schema, pyarrow_to_pandas_schema
import pyarrow as pa

arrow_schema = pa.schema(
    [
        pa.field("column1", pa.int64()),
        pa.field("column2", pa.string()),
    ]
)

polars_schema = pyarrow_to_polars_schema(arrow_schema)
pandas_schema = pyarrow_to_pandas_schema(arrow_schema)
print(polars_schema)
print(pandas_schema)
```

---

## **Learn More**

- [Installation Guide](installation.md)
- [Usage Examples](usage.md)
- [API Reference](api.md)
- [Contributing](contributing.md)

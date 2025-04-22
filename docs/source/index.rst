OMOP Schema
===========

.. image:: https://img.shields.io/pypi/v/omop_schema
   :target: https://pypi.org/project/omop_schema/
   :alt: PyPI Version

.. image:: https://codecov.io/gh/rvandewater/omop_schema/graph/badge.svg?token=RW6JXHNT0W
   :target: https://codecov.io/gh/rvandewater/omop_schema
   :alt: Code Coverage

.. image:: https://github.com/rvandewater/omop_schema/actions/workflows/tests.yaml/badge.svg
   :target: https://github.com/rvandewater/omop_schema/actions/workflows/tests.yaml
   :alt: Tests

`omop_schema` is a Python package designed to read, manage, and convert OMOP (Observational Medical Outcomes Partnership) data into the correct schema. It provides tools to handle OMOP CDM (Common Data Model) tables, convert schemas between different formats, and load datasets efficiently.

Features
--------

- **Schema Management**: Define and manage schemas for OMOP CDM tables for different versions (e.g., 5.3, 5.4).
- **Schema Conversion**: Convert PyArrow schemas to Polars or Pandas-compatible schemas.
- **Dataset Loading**: Load datasets from CSV files into PyArrow tables, ensuring they match the defined schema.
- **Optional Dependencies**: Support for Polars and Pandas as optional dependencies for schema conversion.

Installation
------------

Install the package using `pip`:

.. code-block:: bash

   pip install omop_schema

To include optional dependencies:

.. code-block:: bash

   pip install omop_schema[polars]
   pip install omop_schema[pandas]
   pip install omop_schema[polars,pandas]

Usage
-----

### Define and Retrieve OMOP Schemas

Retrieve the schema for a specific table:

.. code-block:: python

   from omop_schema.schema.v54 import OMOPSchemaV54

   schema_v54 = OMOPSchemaV54()
   concept_schema = schema_v54.get_pyarrow_schema("concept")
   print(concept_schema)

### Load Datasets

Load datasets from a folder containing CSV files:

.. code-block:: python

   from omop_schema.schema.v54 import OMOPSchemaV54

   schema_v54 = OMOPSchemaV54()
   datasets = schema_v54.load_csv_dataset("path/to/csv/folder")

   # Access a specific table
   concept_table = datasets["concept"]
   print(concept_table)

### Convert PyArrow Schema to Polars Schema

Convert a PyArrow schema to a Polars-compatible schema:

.. code-block:: python

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

Contributing
------------

Contributions are welcome! Please open an issue or submit a pull request on the `GitHub repository <https://github.com/rvandewater/omop_schema>`_.

License
-------

This project is licensed under the MIT License. See the `LICENSE <https://github.com/rvandewater/omop_schema/blob/main/LICENSE>`_ file for details.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   autoapi/index
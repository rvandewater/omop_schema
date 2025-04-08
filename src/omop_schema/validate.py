class OMOPValidator:
    def __init__(self, schema_version):
        self.schema = schema_version()._load_schema()

    def validate_table(self, table_name, dataset):
        """
        Validate a dataset against the schema for a specific OMOP table.

        Args:
            table_name (str): The name of the OMOP table to validate.
            dataset (pa.Table): The dataset to validate.

        Returns:
            dict: Validation results with missing and mismatched columns.
        """
        if table_name not in self.schema:
            raise ValueError(f"Table '{table_name}' is not defined in the schema.")

        expected_schema = self.schema[table_name]
        dataset_schema = {field.name: field.type for field in dataset.schema}

        missing_columns = [col for col in expected_schema if col not in dataset_schema]
        mismatched_columns = [
            col
            for col in expected_schema
            if col in dataset_schema and dataset_schema[col] != expected_schema[col]
        ]
        extra_columns = [col for col in dataset_schema if col not in expected_schema]

        return {
            "missing_columns": missing_columns,
            "mismatched_columns": mismatched_columns,
            "extra_columns": extra_columns,
        }

    def load_dataset(self, path, table_name):
        """
        Load the dataset for a specific OMOP table.

        Args:
            table_name (str): The name of the OMOP table to load.

        Returns:
            pa.Table: The loaded dataset.
        """

    def strictly_valid(self):
        """
        Check if the dataset is strictly valid according to the schema.

        Returns:
            bool: True if the dataset is strictly valid, False otherwise.
        """
        for table_name, expected_schema in self.schema.items():
            dataset = self.load_dataset(table_name)
            validation_result = self.validate_table(table_name, dataset)
            if (
                validation_result["missing_columns"]
                or validation_result["mismatched_columns"]
                or validation_result["extra_columns"]
            ):
                return False
        return True

    def base_valid(self):
        """
        Check if the dataset is base valid according to the schema. Excludes checking for extra columns.

        Returns:
            bool: True if the dataset is base valid, False otherwise.
        """
        for table_name, expected_schema in self.schema.items():
            dataset = self.load_dataset(table_name)
            validation_result = self.validate_table(table_name, dataset)
            if validation_result["missing_columns"] or validation_result["mismatched_columns"]:
                return False
        return True

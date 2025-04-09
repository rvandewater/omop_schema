# Initialize the validator
from src.omop_schema.schema.v5_3 import OMOPSchemaV53
from src.omop_schema.validate import OMOPValidator, validate_omop_dataset_graphically

validator = OMOPValidator(OMOPSchemaV53)

# Validate the dataset and display results
validate_omop_dataset_graphically(
    validator,
    "/Users/robin/Documents/datasets/mimic-iv-demo-data-in-the-omop-common-data-model-0.9/1_omop_data_csv",
    load_with_expected_schema=True,
)

# Initialize the validator
from omop_schema.schema.v5_3 import OMOPSchemaV53
from omop_schema.validate import OMOPValidator, validate_omop_dataset_graphically

validator = OMOPValidator(OMOPSchemaV53)

# Validate the dataset and display results
validate_omop_dataset_graphically(
    validator,
    "/sc/arion/projects/hpims-hpi/projects/foundation_models_ehr/cohorts/full_omop/",
    load_with_expected_schema=True,
)

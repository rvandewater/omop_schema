from src.omop_schema.schema.v5_4 import OMOPSchemaV54
from src.omop_schema.schema.v5_3 import OMOPSchemaV53


def get_schema_loader(omop_version):
    """
    Returns the appropriate schema loader based on the OMOP version.
    """
    if omop_version == "5.3" or omop_version == 5.3:
        return OMOPSchemaV53()
    elif omop_version == "5.4" or omop_version == 5.4:
        return OMOPSchemaV54()
    else:
        raise ValueError(f"Unsupported OMOP version: {omop_version}")
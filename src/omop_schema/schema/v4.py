import pyarrow as pa
from src.omop_schema.schema.base import OMOPSchemaBase


class OMOPSchemaV4(OMOPSchemaBase):
    """
    A class to define and manage the schema for OMOP CDM tables for version 4.
    """
    def _load_schema(self):
        return {
            "concept": {
                "concept_id": pa.int64(),
                "concept_name": pa.string(),
                "concept_level": pa.int64(),
                "concept_class": pa.string(),
                "vocabulary_id": pa.int64(),
                "concept_code": pa.string(),
                "valid_start_date": pa.date64(),
                "valid_end_date": pa.date64(),
                "invalid_reason": pa.string(),
            },
            "concept_ancestor": {
                "ancestor_concept_id": pa.int64(),
                "descendant_concept_id": pa.int64(),
                "max_levels_of_separation": pa.int64(),
                "min_levels_of_separation": pa.int64(),
            },
            "concept_relationship": {
                "concept_id_1": pa.int64(),
                "concept_id_2": pa.int64(),
                "relationship_id": pa.int64(),
                "valid_start_date": pa.date64(),
                "valid_end_date": pa.date64(),
                "invalid_reason": pa.string(),
            },
            "concept_synonym": {
                "concept_synonym_id": pa.int64(),
                "concept_id": pa.int64(),
                "concept_synonym_name": pa.string(),
            },
            "drug_strength": {
                "drug_concept_id": pa.int64(),
                "ingredient_concept_id": pa.int64(),
                "amount_value": pa.float64(),
                "amount_unit": pa.string(),
                "concentration_value": pa.float64(),
                "concentration_enum_unit": pa.string(),
                "concentration_denom_unit": pa.string(),
                "valid_start_date": pa.date64(),
                "valid_end_date": pa.date64(),
                "invalid_reason": pa.string(),
            },
            "relationship": {
                "relationship_id": pa.int64(),
                "relationship_name": pa.string(),
                "is_hierarchical": pa.int64(),
                "defines_ancestry": pa.int64(),
                "reverse_relationship": pa.int64(),
            },
            "source_to_concept_map": {
                "source_code": pa.string(),
                "source_vocabulary_id": pa.int64(),
                "source_code_description": pa.string(),
                "target_concept_id": pa.int64(),
                "target_vocabulary_id": pa.int64(),
                "mapping_type": pa.string(),
                "primary_map": pa.string(),
                "valid_start_date": pa.date64(),
                "valid_end_date": pa.date64(),
                "invalid_reason": pa.string(),
            },
            "vocabulary": {
                "vocabulary_id": pa.int64(),
                "vocabulary_name": pa.string(),
            },
        }
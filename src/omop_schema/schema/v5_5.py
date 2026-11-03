import pyarrow as pa

from .v5_4 import OMOPSchemaV54


class OMOPSchemaV55(OMOPSchemaV54):
    """
    OMOP CDM 5.5: CDM 5.4 plus the fields and tables in
    https://ohdsi.github.io/CommonDataModel/cdm55Changes.html.

    CDM 5.5 only adds optional fields to measurement, observation, specimen and cdm_source, and three
    vocabulary-metadata tables; nothing is renamed or removed.

    Examples:
        >>> schema = OMOPSchemaV55()
        >>> schema.get_schema("observation")["value_as_date"], schema.get_schema("pack_content")["box_size"]
        (DataType(date64[ms]), DataType(int64))
    """

    version = "5.5"

    def _load_schema(self):
        schemas = super()._load_schema()
        added_fields = {
            "measurement": {"value_as_source_concept_id": pa.int64()},
            "observation": {
                "value_as_date": pa.date64(),
                "unit_source_concept_id": pa.int64(),
                "value_as_source_concept_id": pa.int64(),
            },
            "specimen": {"visit_occurrence_id": pa.int64(), "visit_detail_id": pa.int64()},
            "cdm_source": {"cdm_release_identifier": pa.string()},
        }
        for table, fields in added_fields.items():
            schemas[table] = {**schemas[table], **fields}
        schemas.update(
            {
                "pack_content": {
                    "pack_concept_id": pa.int64(),
                    "drug_concept_id": pa.int64(),
                    "amount": pa.int64(),
                    "box_size": pa.int64(),
                },
                "concept_metadata": {
                    "concept_id": pa.int64(),
                    "concept_category": pa.string(),
                    "reuse_status": pa.string(),
                },
                "concept_relationship_metadata": {
                    "concept_id_1": pa.int64(),
                    "concept_id_2": pa.int64(),
                    "relationship_id": pa.string(),
                    "relationship_predicate_id": pa.string(),
                    "relationship_group": pa.int64(),
                    "mapping_source": pa.string(),
                    "confidence": pa.float64(),
                    "mapping_tool": pa.string(),
                    "mapper": pa.string(),
                    "reviewer": pa.string(),
                },
            }
        )
        return schemas

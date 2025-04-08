import pyarrow as pa

from src.omop_schema.schema.v5_3 import OMOPSchemaV53


# Based on : https://ohdsi.github.io/CommonDataModel/cdm54Changes.html
class OMOPSchemaV54(OMOPSchemaV53):
    def _load_schema(self):
        schemas = super()._load_schema()
        schemas.update(
            {
                "visit_occurrence": {
                    "visit_occurrence_id": pa.int64(),
                    "person_id": pa.int64(),
                    "visit_concept_id": pa.int64(),
                    "visit_start_date": pa.date64(),
                    "visit_start_datetime": pa.timestamp("us"),
                    "visit_end_date": pa.date64(),
                    "visit_end_datetime": pa.timestamp("us"),
                    "visit_type_concept_id": pa.int64(),
                    "provider_id": pa.int64(),
                    "care_site_id": pa.int64(),
                    "visit_source_value": pa.string(),
                    "visit_source_concept_id": pa.int64(),
                    "admitted_from_concept_id": pa.int64(),
                    "admitted_from_source_value": pa.string(),
                    "discharged_to_concept_id": pa.int64(),
                    "discharged_to_source_value": pa.string(),
                    "preceding_visit_occurrence_id": pa.int64(),
                },
                "visit_detail": {
                    "visit_detail_id": pa.int64(),
                    "person_id": pa.int64(),
                    "visit_detail_concept_id": pa.int64(),
                    "visit_detail_start_date": pa.date64(),
                    "visit_detail_start_datetime": pa.timestamp("us"),
                    "visit_detail_end_date": pa.date64(),
                    "visit_detail_end_datetime": pa.timestamp("us"),
                    "visit_detail_type_concept_id": pa.int64(),
                    "provider_id": pa.int64(),
                    "care_site_id": pa.int64(),
                    "visit_detail_source_value": pa.string(),
                    "visit_detail_source_concept_id": pa.int64(),
                    "admitted_from_concept_id": pa.int64(),
                    "admitted_from_source_value": pa.string(),
                    "discharged_to_concept_id": pa.int64(),
                    "discharged_to_source_value": pa.string(),
                    "parent_visit_detail_id": pa.int64(),
                    "visit_occurrence_id": pa.int64(),
                },
                "procedure_occurrence": {
                    "procedure_occurrence_id": pa.int64(),
                    "person_id": pa.int64(),
                    "procedure_concept_id": pa.int64(),
                    "procedure_date": pa.date64(),
                    "procedure_datetime": pa.timestamp("us"),
                    "procedure_end_date": pa.date64(),
                    "procedure_end_datetime": pa.timestamp("us"),
                    "procedure_type_concept_id": pa.int64(),
                    "modifier_concept_id": pa.int64(),
                    "quantity": pa.int64(),
                    "provider_id": pa.int64(),
                    "visit_occurrence_id": pa.int64(),
                    "visit_detail_id": pa.int64(),
                    "procedure_source_value": pa.string(),
                    "procedure_source_concept_id": pa.int64(),
                    "modifier_source_value": pa.string(),
                },
                "device_exposure": {
                    "device_exposure_id": pa.int64(),
                    "person_id": pa.int64(),
                    "device_concept_id": pa.int64(),
                    "device_exposure_start_date": pa.date64(),
                    "device_exposure_start_datetime": pa.timestamp("us"),
                    "device_exposure_end_date": pa.date64(),
                    "device_exposure_end_datetime": pa.timestamp("us"),
                    "device_type_concept_id": pa.int64(),
                    "unique_device_id": pa.string(),
                    "quantity": pa.int64(),
                    "provider_id": pa.int64(),
                    "visit_occurrence_id": pa.int64(),
                    "visit_detail_id": pa.int64(),
                    "device_source_value": pa.string(),
                    "device_source_concept_id": pa.int64(),
                    "production_id": pa.string(),
                    "unit_concept_id": pa.int64(),
                    "unit_source_value": pa.string(),
                    "unit_source_concept_id": pa.int64(),
                },
                "measurement": {
                    "measurement_id": pa.int64(),
                    "person_id": pa.int64(),
                    "measurement_concept_id": pa.int64(),
                    "measurement_date": pa.date64(),
                    "measurement_datetime": pa.timestamp("us"),
                    "measurement_time": pa.string(),
                    "measurement_type_concept_id": pa.int64(),
                    "operator_concept_id": pa.int64(),
                    "value_as_number": pa.float64(),
                    "value_as_concept_id": pa.int64(),
                    "unit_concept_id": pa.int64(),
                    "range_low": pa.float64(),
                    "range_high": pa.float64(),
                    "provider_id": pa.int64(),
                    "visit_occurrence_id": pa.int64(),
                    "visit_detail_id": pa.int64(),
                    "measurement_source_value": pa.string(),
                    "measurement_source_concept_id": pa.int64(),
                    "unit_source_value": pa.string(),
                    "value_source_value": pa.string(),
                    "unit_source_concept_id": pa.int64(),
                    "measurement_event_id": pa.int64(),
                    "meas_event_field_concept_id": pa.int64(),
                },
                "observation": {
                    "observation_id": pa.int64(),
                    "person_id": pa.int64(),
                    "observation_concept_id": pa.int64(),
                    "observation_date": pa.date64(),
                    "observation_datetime": pa.timestamp("us"),
                    "observation_type_concept_id": pa.int64(),
                    "value_as_number": pa.float64(),
                    "value_as_string": pa.string(),
                    "value_as_concept_id": pa.int64(),
                    "qualifier_concept_id": pa.int64(),
                    "unit_concept_id": pa.int64(),
                    "provider_id": pa.int64(),
                    "visit_occurrence_id": pa.int64(),
                    "visit_detail_id": pa.int64(),
                    "observation_source_value": pa.string(),
                    "observation_source_concept_id": pa.int64(),
                    "unit_source_value": pa.string(),
                    "qualifier_source_value": pa.string(),
                    "value_source_value": pa.string(),
                    "observation_event_id": pa.int64(),
                    "obs_event_field_concept_id": pa.int64(),
                },
                "note": {
                    "note_id": pa.int64(),
                    "person_id": pa.int64(),
                    "note_date": pa.date64(),
                    "note_datetime": pa.timestamp("us"),
                    "note_type_concept_id": pa.int64(),
                    "note_class_concept_id": pa.int64(),
                    "note_title": pa.string(),
                    "note_text": pa.string(),
                    "encoding_concept_id": pa.int64(),
                    "language_concept_id": pa.int64(),
                    "provider_id": pa.int64(),
                    "visit_occurrence_id": pa.int64(),
                    "visit_detail_id": pa.int64(),
                    "note_source_value": pa.string(),
                    "note_event_id": pa.int64(),
                    "note_event_field_concept_id": pa.int64(),
                },
                "location": {
                    "location_id": pa.int64(),
                    "address_1": pa.string(),
                    "address_2": pa.string(),
                    "city": pa.string(),
                    "state": pa.string(),
                    "zip": pa.string(),
                    "county": pa.string(),
                    "location_source_value": pa.string(),
                    "country_concept_id": pa.int64(),
                    "country_source_value": pa.string(),
                    "latitude": pa.float64(),
                    "longitude": pa.float64(),
                },
                "metadata": {
                    "metadata_concept_id": pa.int64(),
                    "metadata_type_concept_id": pa.int64(),
                    "name": pa.string(),
                    "value_as_string": pa.string(),
                    "value_as_concept_id": pa.int64(),
                    "metadata_date": pa.date64(),
                    "metadata_datetime": pa.timestamp("us"),
                    "metadata_id": pa.int64(),
                    "value_as_number": pa.float64(),
                },
                "cdm_source": {
                    "cdm_source_name": pa.string(),
                    "cdm_source_abbreviation": pa.string(),
                    "cdm_holder": pa.string(),
                    "source_description": pa.string(),
                    "source_documentation_reference": pa.string(),
                    "cdm_etl_reference": pa.string(),
                    "source_release_date": pa.date64(),
                    "cdm_release_date": pa.date64(),
                    "cdm_version": pa.string(),
                    "vocabulary_version": pa.string(),
                    "cdm_version_concept_id": pa.int64(),
                },
                "vocabulary": {
                    "vocabulary_id": pa.string(),
                    "vocabulary_name": pa.string(),
                    "vocabulary_reference": pa.string(),
                    "vocabulary_version": pa.string(),
                    "vocabulary_concept_id": pa.int64(),
                },
                "cohort": {
                    "cohort_definition_id": pa.int64(),
                    "subject_id": pa.int64(),
                    "cohort_start_date": pa.date64(),
                    "cohort_end_date": pa.date64(),
                },
                "episode": {
                    "episode_id": pa.int64(),
                    "person_id": pa.int64(),
                    "episode_concept_id": pa.int64(),
                    "episode_start_date": pa.date64(),
                    "episode_start_datetime": pa.timestamp("us"),
                    "episode_end_date": pa.date64(),
                    "episode_end_datetime": pa.timestamp("us"),
                    "episode_parent_id": pa.int64(),
                    "episode_number": pa.int64(),
                    "episode_object_concept_id": pa.int64(),
                    "episode_type_concept_id": pa.int64(),
                    "episode_source_value": pa.string(),
                    "episode_source_concept_id": pa.int64(),
                },
                "episode_event": {
                    "episode_id": pa.int64(),
                    "event_id": pa.int64(),
                    "episode_event_field_concept_id": pa.int64(),
                },
            }
        )
        return schemas

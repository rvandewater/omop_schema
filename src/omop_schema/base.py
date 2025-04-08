from abc import ABC, abstractmethod


class OMOPSchemaBase(ABC):
    """
    Abstract base class to define and manage the schema for OMOP CDM tables.
    """
    def __init__(self):
        self.schemas = self._load_schema()

    @abstractmethod
    def _load_schema(self):
        """
        Load the schema for the OMOP CDM tables.
        This method should be implemented by subclasses.
        """
        pass

    def get_schema(self, table_name):
        return self.schemas.get(table_name, {})

    # def read_csv(self, file_path, table_name):
    #     schema = self.get_schema(table_name)
    #     return #pl.read_csv(file_path, dtypes=schema)

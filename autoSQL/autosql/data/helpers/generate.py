import logging
from typing import Optional, Dict, List, Union

from faker import Faker

logger = logging.getLogger(__name__)


class DataGenerator:
    """A helper class for generating data for the autoSQL dataset"""

    def __init__(self) -> None:
        """Initializes the class"""

        self.fake = Faker()

    def __repr__(self):
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in self.__dict__)
        return "{}({})".format(type(self).__name__, ", ".join(items))

    #################################
    # Data Generation Functions     #
    #################################

    def generate_random_data(self, data_type) -> Union[str, int, None]:
        """Generates random data for a given data type. Currently only supports VARCHAR and INT data types.

        :param data_type: The data type to generate random data for
        :type data_type: str
        :return: Random data for a given data type
        :rtype: str, int, or None
        """

        if data_type == "VARCHAR":
            return self.fake.name()
        elif data_type == "INT":
            return self.fake.random_int(min=1, max=100)
        else:
            logger.warning(f"Data type {data_type} is not supported. Returning None.")
            return None

    def generate_filler_data(
        self, column_types, num_records=5
    ) -> Dict[str, List[Dict[str, Union[str, int, None]]]]:
        """Generates filler data for a given set of column types. Currently only supports VARCHAR and INT data types.

        :param column_types: The column types to generate filler data for
        :type column_types: dict {"table_name": {"column_name": "column_type"}}
        :param num_records: The number of records to generate for each table, defaults to 5
        :type num_records: int, optional
        :return: Filler data for a given set of column types
        :rtype: dict {"table_name": [{"column_name": generate_random_data()}, ... num_records]}
        """

        filler_data = {}

        for table_name, columns in column_types.items():
            filler_data[table_name] = []

            for _ in range(num_records):
                record = {}
                for column_name, data_type in columns.items():
                    record[column_name] = self.generate_random_data(data_type)
                filler_data[table_name].append(record)

        return filler_data

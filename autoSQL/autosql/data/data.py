import json
import logging
from typing import Optional, Dict, List, Union

from datasets import load_dataset, Dataset, DatasetDict

import sqlglot
from sqlglot.executor import execute
from sqlglot.errors import ExecuteError, TokenError, SchemaError, ExecuteError, ParseError, UnsupportedError, SqlglotError, OptimizeError

from .helpers import DataGenerator

logger = logging.getLogger(__name__)

class SQLData:
    """This class handles the ETL process for SQL data:
            
    Data is expected to be structured, at a minimum, as follows:
        DatasetDict({
            train: Dataset({
                features: ['answer', 'context', 'question'],
                num_rows: 78577
            })
        })

    Features are expected to be structured as follows:
        {
            'answer': 'SELECT COUNT(*) FROM head WHERE age > 56',
            'context': 'CREATE TABLE head (age INTEGER)',
            'question': 'How many heads of the departments are older than 56 ?',
        }
    """ 

    def __init__(self) -> None:
        """Initializes the class"""
        
        self.data = {}
        self.data_generator = DataGenerator()

    def __repr__(self):
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in self.__dict__)
        return "{}({})".format(type(self).__name__, ", ".join(items))
    
    @classmethod
    def from_dataset(cls, dataset_name: str, subset: bool = False, subset_value: int = 1000) -> "SQLData":
        """Creates a class instance from a dataset name

        :param dataset_name: The name of the dataset to create a class instance from
        :type dataset_name: str
        :param subset: Whether or not to load a subset of the dataset, defaults to False
        :type subset: bool, optional
        :param subset_value: The number of records to load if subset=True, defaults to 1000
        :type subset_value: int, optional
        :return: A class instance
        :rtype: SQLData
        """

        instance = cls()
        instance.load_data(dataset_name=dataset_name, subset=subset, subset_value=subset_value)
        return instance

    #################################
    # Data Extraction Functions     #
    #################################

    def load_data(self, dataset_name: str, subset: bool = False, subset_value: int = 1000) -> None:
        """Loads data from the HuggingFace datasets library. Stores the data in the class instance self.data = {"dataset_name": dataset}.
        
        :param dataset_name: The name of the dataset to load
        :type dataset_name: str
        :param subset: Whether or not to load a subset of the dataset, defaults to False
        :type subset: bool, optional
        :param subset_value: The number of records to load if subset=True, defaults to 1000
        :type subset_value: int, optional
        """

        dataset = load_dataset(dataset_name)

        if subset: 
            keys = list(dataset.keys())
            for key in keys:
                dataset[key] = dataset[key].select(range(subset_value))

        self.data[dataset_name] = dataset

    #################################
    # Data Transformation Functions #
    #################################  

    @staticmethod
    def _blanket_answer_syntax(dataset) -> Dict[str, str]:
        """Replaces double quotes with single quotes in the answer column of a dataset, intended to correct syntax errors in the answer column
        
        :param dataset: The dataset to replace double quotes with single quotes in the answer column
        :type dataset: datasets.Dataset
        :return: A dictionary containing the answer with double quotes replaced with single quotes
        :rtype: dict {"answer": str}
        """

        try:
            answer = dataset['answer'].replace('"', "'")
        except Exception as e:
            logger.error(f"An error occured while trying to load the answer: {e}")
            raise

        return {"answer": answer}

    @staticmethod
    def _compute_table_count(dataset) -> Dict[str, int]: 
        """Computes the number of tables created within the context of a datum
        
        :param dataset: The dataset to compute the number of tables created within the context of a datum
        :type dataset: datasets.Dataset
        :return: A dictionary containing the number of tables created within the context of a datum
        :rtype: dict {"table_count": int}
        """

        try:
            count = len(dataset['context'].split(';'))
        except Exception as e:
            logger.error(f"An error occured while trying to compute the table count: {e}")
            raise
    
        return {"table_count": count}
    
    @staticmethod
    def _abstract_column_types(dataset) -> Dict[str, Dict[str, str]]: 
        """Abstracts the column types for every CREATE table statement from the context of a datum
        
        :param dataset: The dataset to abstract the column types for every CREATE table statement from the context of a datum
        :type dataset: datasets.Dataset
        :return: A dictionary containing the column types for every CREATE table statement from the context of a datum
        :rtype: dict {"column_types": {"table_name": {"column_name": "column_type"}}
        """
        
        try:
            atls = sqlglot.parse(dataset['context'])
        except Exception as e:
            logger.error(f"An error occured while trying to parse the context: {e}")
            raise

        tables = {}

        for atl in atls:
            column_types = {}
            table_name = atl.find(sqlglot.expressions.Identifier).this
            for expr in atl.this.expressions:
                column_name = expr.find(sqlglot.expressions.Identifier).this
                column_type = expr.find(sqlglot.expressions.DataType).this.value
                column_types[column_name] = column_type
            tables[table_name] = column_types

        return {"column_types": json.dumps(tables)}
    
    @staticmethod
    def _identify_duplicate_create_table(dataset) -> Dict[str, bool]: 
        """Identifies whether or not a CREATE table statement is duplicated within the context of a datum
        
        :param dataset: The dataset to identify whether or not a CREATE table statement is duplicated within the context of a datum
        :type dataset: datasets.Dataset
        :return: A dictionary containing whether or not a CREATE table statement is duplicated within the context of a datum
        :rtype: dict {"duplicate_create_table": bool}
        """

        try:
            create_count = dataset['table_count']
        except KeyError:
            logger.warning("The key 'table_count' does not exist in the dataset. Preprocess the dataset with the function _compute_table_count(dataset) to create the key 'table_count'.")
            raise
            # dataset = dataset.map(SQLData._compute_table_count) TODO: KeyError fallbacks 
        except Exception as e:
            logger.error(f"An error occured while trying to load the table count: {e}")
            raise 

        try:
            table_count = len(json.loads(dataset['column_types']).keys())
        except KeyError:
            logger.warning("The key 'column_types' does not exist in the dataset. Preprocess the dataset with the function _abstract_column_types(dataset) to create the key 'column_types'.")
            raise
            # dataset = dataset.map(SQLData._abstract_column_types) TODO: KeyError fallbacks 
        except Exception as e:
            logger.error(f"An error occured while trying to load the column types: {e}")
            raise

        if create_count == table_count:
            return {"duplicate_create_table": False}
        else:
            return {"duplicate_create_table": True}
        
    def _populate_data(self, dataset) -> Dict[str, Dict[str, List[Dict[str, Union[str, int, None]]]]]: 
        """Creates a dictionary containing randomly generated data based upon the provided column types for a CREATE table statement from the context of a datum
        
        :param dataset: The dataset to create a dictionary containing randomly generated data based upon the provided column types for a CREATE table statement from the context of a datum
        :type dataset: datasets.Dataset
        :return: A dictionary containing randomly generated data based upon the provided column types for a CREATE table statement from the context of a datum
        :rtype: dict {"filler_data": {"table_name": [{"column_name": generate_random_data()}, ... num_records]}}
        """
        
        try:
            column_types = json.loads(dataset['column_types'])
        except KeyError:
            logger.warning("The key 'column_types' does not exist in the dataset. Preprocess the dataset with the function _abstract_column_types(dataset) to create the key 'column_types'.")
            raise
            # dataset = dataset.map(SQLData._abstract_column_types) TODO: KeyError fallbacks 
        except Exception as e:
            logger.error(f"An error occured while trying to load the column types: {e}")
            raise 

        return {"filler_data": json.dumps(self.data_generator.generate_filler_data(column_types))}
    
    @staticmethod
    def validate_query(dataset) -> Dict[str, Union[str, bool]]:
        """Validates the query against the provided filler data and returns the query result

        :param dataset: The dataset to validate the query against the provided filler data and returns the query result
        :type dataset: datasets.Dataset
        :return: A dictionary containing the query result and whether or not the query is valid
        :rtype: dict {"query_result": str, "valid_query": bool}
        """

        try:
            tables = json.loads(dataset['filler_data'])
        except KeyError:
            logger.warning("The key 'filler_data' does not exist in the dataset. Preprocess the dataset with the function _populate_data(dataset) to create the key 'filler_data'.")
            raise
            # dataset = dataset.map(SQLData._populate_data) TODO: KeyError fallbacks 
        except Exception as e:
            logger.error(f"An error occured while trying to load the filler data: {e}")
            raise

        try:
            query = dataset['answer']
        except Exception as e:
            logger.error(f"An error occured while trying to load the query: {e}")
            raise

        try:
            result = execute(query, tables=tables)
            result = str(result.rows) if result.rows is not None else ''
            return {"query_result": result, "valid_query": True}
        except ExecuteError as e:
            return {"query_result": "ExecuteError", "valid_query": False}
        except OptimizeError as e:
            return {"query_result": "OptimizeError", "valid_query": False}
        except TokenError as e:
            return {"query_result": "TokenError", "valid_query": False}
        except SchemaError as e:
            return {"query_result": "SchemaError", "valid_query": False}
        except ParseError as e:
            return {"query_result": "ParseError", "valid_query": False}
        except UnsupportedError as e:
            return {"query_result": "UnsupportedError", "valid_query": False}
        except SqlglotError as e: 
            return {"query_result": "SqlglotError", "valid_query": False}
        except Exception as e:
            return {"query_result": str(e), "valid_query": False}
        
    def preprocess_data(
        self, 
        dataset_name: str, 
        blanket_answer_syntax: bool = True,
        compute_table_count: bool = True,
        abstract_column_types: bool = True,
        identify_duplicate_create_table: bool = True,
        populate_data: bool = True,
        validate_query: bool = True
    ) -> None:
        """Preprocesses the data by applying the following functions to the dataset:
            - _blanket_answer_syntax(dataset)
            - _compute_table_count(dataset)
            - _abstract_column_types(dataset)
            - _identify_duplicate_create_table(dataset)
            - _populate_data(dataset)
            - validate_query(dataset)

        :param dataset_name: The name of the dataset to preprocess
        :type dataset_name: str
        :param blanket_answer_syntax: Whether or not to replace double quotes with single quotes in the answer column of a dataset, intended to correct syntax errors in the answer column, defaults to True
        :type blanket_answer_syntax: bool, optional
        :param compute_table_count: Whether or not to compute the number of tables created within the context of a datum, defaults to True
        :type compute_table_count: bool, optional
        :param abstract_column_types: Whether or not to abstract the column types for every CREATE table statement from the context of a datum, defaults to True
        :type abstract_column_types: bool, optional
        :param identify_duplicate_create_table: Whether or not to identify whether or not a CREATE table statement is duplicated within the context of a datum, defaults to True
        :type identify_duplicate_create_table: bool, optional
        :param populate_data: Whether or not to create a dictionary containing randomly generated data based upon the provided column types for a CREATE table statement from the context of a datum, defaults to True
        :type populate_data: bool, optional
        :param validate_query: Whether or not to validate the query against the provided filler data and returns the query result, defaults to True
        :type validate_query: bool, optional
        """
        
        if dataset_name not in self.data.keys():
            logger.warning(f"The dataset {dataset_name} has not been loaded. Loading the dataset with the function load_data(dataset_name).")
            self.load_data(dataset_name)
        
        dataset = self.data[dataset_name]

        if blanket_answer_syntax:
            logger.info(f"Preprocessing the dataset with the function _blanket_answer_syntax(dataset).")
            dataset = dataset.map(SQLData._blanket_answer_syntax)
        
        if compute_table_count:
            logger.info(f"Preprocessing the dataset with the function _compute_table_count(dataset).")
            dataset = dataset.map(SQLData._compute_table_count)
        
        if abstract_column_types:
            logger.info(f"Preprocessing the dataset with the function _abstract_column_types(dataset).")
            dataset = dataset.map(SQLData._abstract_column_types)
        
        if identify_duplicate_create_table:
            logger.info(f"Preprocessing the dataset with the function _identify_duplicate_create_table(dataset).")
            dataset = dataset.map(SQLData._identify_duplicate_create_table)
        
        if populate_data:
            logger.info(f"Preprocessing the dataset with the function _populate_data(self, dataset).")
            dataset = dataset.map(self._populate_data)
        
        if validate_query:
            logger.info(f"Preprocessing the dataset with the function validate_query(dataset).")
            dataset = dataset.map(SQLData.validate_query)

        self.data[dataset_name] = dataset

    def filter_data(
        self, 
        dataset_name: str,
        drop_invalid_query: bool = True,
        drop_duplicate_tables: bool = True,
        drop_empty_query_result: bool = False,
        update_class_dataset: bool = True,
    ) -> Optional[Union[DatasetDict, None]]:
        
        if dataset_name not in self.data.keys():
            logger.warning(f"The dataset {dataset_name} has not been loaded. Loading the dataset with the function load_data(dataset_name).")
            self.load_data(dataset_name)
        
        dataset = self.data[dataset_name]

        if drop_invalid_query:
            try: 
                dataset = dataset.filter(lambda x: x['valid_query'] == True)
            except KeyError:
                logger.warning("The key 'valid_query' does not exist in the dataset. Preprocess the dataset with the function validate_query(dataset) to create the key 'valid_query'.")
                raise
                # dataset = dataset.map(SQLData.validate_query) TODO: KeyError fallbacks 
                # dataset = dataset.filter(lambda x: x['valid_query'] == True) 
            except Exception as e:
                logger.error(f"An error occured while trying to filter the dataset: {e}")
                raise

        if drop_duplicate_tables:
            try:
                dataset = dataset.filter(lambda x: x['duplicate_create_table'] == False)
            except KeyError:
                logger.warning("The key 'duplicate_create_table' does not exist in the dataset. Preprocess the dataset with the function _identify_duplicate_create_table(dataset) to create the key 'duplicate_create_table'.")
                raise
                # dataset = dataset.map(SQLData._identify_duplicate_create_table) TODO: KeyError fallbacks 
                # dataset = dataset.filter(lambda x: x['duplicate_create_table'] == False)
            except Exception as e:
                logger.error(f"An error occured while trying to filter the dataset: {e}")
                raise
        
        if drop_empty_query_result:
            try:
                dataset = dataset.filter(lambda x: x['query_result'] != '[]')
            except KeyError:
                logger.warning("The key 'query_result' does not exist in the dataset. Preprocess the dataset with the function validate_query(dataset) to create the key 'query_result'.")
                raise
                # dataset = dataset.map(SQLData.validate_query) TODO: KeyError fallbacks 
                # dataset = dataset.filter(lambda x: x['query_result'] != '[]')
            except Exception as e:
                logger.error(f"An error occured while trying to filter the dataset: {e}")
                raise

        if update_class_dataset:
            self.data[dataset_name] = dataset
            return None
        else: 
            return dataset

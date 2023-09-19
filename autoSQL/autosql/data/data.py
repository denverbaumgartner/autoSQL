import json
import logging
from typing import Optional, Dict, List, Union

from datasets import load_dataset

import sqlglot
from sqlglot.executor import execute
from sqlglot.errors import ExecuteError, TokenError, SchemaError, ExecuteError, ParseError, UnsupportedError, SqlglotError, OptimizeError

from helpers import DataGenerator

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
        """Initializes the class

        """
        
        self.data = {}
        self.data_generator = DataGenerator()

    def __repr__(self):
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in self.__dict__)
        return "{}({})".format(type(self).__name__, ", ".join(items))

    #################################
    # Data Extraction Functions     #
    #################################

    def load_data(self, dataset_name: str) -> None:
        """Loads data from the HuggingFace datasets library. Stores the data in the class instance self.data = {"dataset_name": dataset}.
        
        :param dataset_name: The name of the dataset to load
        :type dataset_name: str
        """

        self.data[dataset_name] = load_dataset(dataset_name)

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

        answer = dataset['answer'].replace('"', "'")
        return {"answer": answer}

    @staticmethod
    def _compute_table_count(dataset) -> Dict[str, int]: 
        """Computes the number of tables created within the context of a datum
        
        :param dataset: The dataset to compute the number of tables created within the context of a datum
        :type dataset: datasets.Dataset
        :return: A dictionary containing the number of tables created within the context of a datum
        :rtype: dict {"table_count": int}
        """

        count = len(dataset['context'].split(';'))
        return {"table_count": count}
    
    @staticmethod
    def _abstract_column_types(dataset) -> Dict[str, Dict[str, str]]: 
        """Abstracts the column types for every CREATE table statement from the context of a datum
        
        :param dataset: The dataset to abstract the column types for every CREATE table statement from the context of a datum
        :type dataset: datasets.Dataset
        :return: A dictionary containing the column types for every CREATE table statement from the context of a datum
        :rtype: dict {"column_types": {"table_name": {"column_name": "column_type"}}
        """
        
        atls = sqlglot.parse(dataset['context'])
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
            logger.warning("The key 'table_count' does not exist in the dataset. Preprocessing the dataset with the function _compute_table_count(dataset) to create the key 'table_count'.")
            dataset = dataset.map(SQLData._compute_table_count)
        except Exception as e:
            logger.error(f"An error occured while trying to load the table count: {e}")
            raise 

        table_count = len(json.loads(dataset['column_types']).keys())

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
            logger.warning("The key 'column_types' does not exist in the dataset. Preprocessing the dataset with the function _abstract_column_types(dataset) to create the key 'column_types'.")
            dataset = dataset.map(SQLData._abstract_column_types)
        except Exception as e:
            logger.error(f"An error occured while trying to load the column types: {e}")
            raise 

        return {"filler_data": json.dumps(self.data_generator.generate_filler_data(column_types))}
    
    def validate_query(dataset) -> Dict[Union[str, bool]]:
        """Validates the query against the provided filler data and returns the query result

        :param dataset: The dataset to validate the query against the provided filler data and returns the query result
        :type dataset: datasets.Dataset
        :return: A dictionary containing the query result and whether or not the query is valid
        :rtype: dict {"query_result": str, "valid_query": bool}
        """

        tables = json.loads(dataset['filler_data'])
        query = dataset['answer']

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
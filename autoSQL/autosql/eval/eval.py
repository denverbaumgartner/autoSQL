import re
import json
import logging
from _decimal import Decimal
from typing import Optional, Dict, List, Union

from datasets import load_dataset, Dataset, DatasetDict

import sqlglot
from sqlglot.executor import execute
from sqlglot.errors import (
    ExecuteError,
    TokenError,
    SchemaError,
    ExecuteError,
    ParseError,
    UnsupportedError,
    SqlglotError,
    OptimizeError,
)

logger = logging.getLogger(__name__)

class SQLEval: 
    """A class for evaluating the performance of model inferences on SQL datasets"""

    def __init__(self) -> None:
        pass 

    def __repr__(self):
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in self.__dict__)
        return "{}({})".format(type(self).__name__, ", ".join(items))

    ########################################
    # Validation and Evaluation Methods    #          
    ########################################

    @staticmethod
    def validate_openai_query(
        dataset: Dataset, 
        query_label: str="openai_inference", 
        data_label: str="filler_data", 
        result_label: str="openai_result", 
        valid_label: str="openai_valid"
    ):
        """Validates the query against the provided filler data and returns the query result
        
        :param dataset: The dataset item to validate.
        :type dataset: dict
        :return: A dictionary containing the query result and whether or not the query is valid
        :rtype: dict {result_label: str, valid_label: bool}
        """
        
        try:
            tables = json.loads(dataset[data_label])
            query = dataset[query_label]["choices"][0]["message"]['content']
            result = execute(query, tables=tables)
            dataset[result_label] = str(result.rows) if result.rows is not None else ""
            dataset[valid_label] = True
            return dataset
        except (ExecuteError, OptimizeError, TokenError, SchemaError, ParseError, UnsupportedError, SqlglotError) as specific_error:
            dataset[result_label] = type(specific_error).__name__
            dataset[valid_label] = False
            return dataset
        except Exception as general_error:
            dataset[result_label] = str(general_error)
            dataset[valid_label] = False
            return dataset
        
    @staticmethod
    def validate_replicate_query(
        dataset: Dataset,
        query_label: str="replicate_inference",
        data_label: str="filler_data",
        result_label: str="replicate_result",
        valid_label: str="replicate_valid",
    ):
        """Validates the query against the provided filler data and returns the query result
        
        :param dataset: The dataset item to validate.
        :type dataset: dict
        :return: A dictionary containing the query result and whether or not the query is valid
        :rtype: dict {result_label: str, valid_label: bool}
        """
        
        try:
            tables = json.loads(dataset[data_label])
            query = dataset[query_label]
            result = execute(query, tables=tables)
            dataset[result_label] = str(result.rows) if result.rows is not None else ""
            dataset[valid_label] = True
            return dataset
        except (ExecuteError, OptimizeError, TokenError, SchemaError, ParseError, UnsupportedError, SqlglotError) as specific_error:
            dataset[result_label] = type(specific_error).__name__
            dataset[valid_label] = False
            return dataset
        except Exception as general_error:
            dataset[result_label] = str(general_error)
            dataset[valid_label] = False
            return dataset
        
    @staticmethod
    def inference_result_check(
        dataset: Dataset,
    ): 
        """Checks the results of the inference against the correct result and returns the result of the check

        :param dataset: The dataset item to check.
        :type dataset: dict
        :return: A dictionary containing the result of the check
        :rtype: dict {openai_correct: bool, replicate_correct: bool, openai_replicate_match: bool}
        """
        
        try: 
            openai_result = dataset['openai_result']
            replicate_result = dataset['replicate_result']
            correct_result = dataset['query_result']

            dataset['openai_correct'] = openai_result == correct_result
            dataset['replicate_correct'] = replicate_result == correct_result
            dataset['openai_replicate_match'] = openai_result == replicate_result
            return dataset
        except Exception as e:
            logger.warning(f"Result check failed with error: {e}")
            raise e

    @staticmethod        
    def replicate_response_parser(dataset): # TODO: update to allow for regex values to be passed in
        """Parses the replicate inference to find a valid SQL query and returns the parsed query and result

        currently, utilizes the regex pattern: r"SELECT.*?(?=\n|\[/|,\[INST\])"

        :param dataset: The dataset item to parse.
        :type dataset: dict
        :return: A dictionary containing the parsed query and result
        :rtype: dict {replicate_inference: str, replicate_result: str}
        """

        
        replicate_inference = dataset['replicate_inference']
        replicate_result = dataset['replicate_result']
        
        tables = json.loads(dataset['filler_data'])
        
        pattern = r"SELECT.*?(?=\n|\[/|,\[INST\])"
        matches = re.findall(pattern, replicate_inference, re.DOTALL)
        
        result = None
        valid_result = None 
        valid_statement = None
        
        for match in matches:
            try: 
                result = execute(match, tables=tables)
                if result.rows is not None: 
                    valid_result = str(result.rows)
                    valid_statement = match
            except:
                pass

        if valid_result and valid_statement: 
            dataset['replicate_inference'] = valid_statement 
            dataset['replicate_result'] = valid_result 
            dataset['replicate_valid'] = True
        else: 
            dataset['replicate_inference'] = replicate_inference 
            dataset['replicate_result'] = replicate_result
            dataset['replicate_valid'] = False
        return dataset

        

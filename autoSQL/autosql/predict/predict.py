import json
import logging
from _decimal import Decimal
from typing import Optional, Dict, List, Union

import openai
from openai.openai_object import OpenAIObject

import sqlglot
from datasets import DatasetDict, Dataset

from .helper import Prompts

logger = logging.getLogger(__name__)

class SQLPredict: 
    """This class handles the dispatching of inference requests to various models. 
    """

    def __init__(
        self, 
        openai_api_key: str,
    ) -> None:
        """Initialize the class"""

        openai.api_key = openai_api_key

        self.openai = openai
        self.prompts = Prompts()

    def __repr__(self):
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in self.__dict__)
        return "{}({})".format(type(self).__name__, ", ".join(items))

    #########################################
    # Request Construction Methods          #
    #########################################

    def _openai_sql_data_structure(
        self, 
        user_context: str,
        user_question: str,
        user_answer: str,
        system_context: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """Constructs a SQL data structure request for OpenAI's API.
        
        :param user_context: The context of the SQL query.
        :type user_context: str
        :param user_question: The question of the SQL query.
        :type user_question: str
        :param user_answer: The answer of the SQL query.
        :type user_answer: str
        :param system_context: The context of the SQL query, None results in class default
        :type system_context: Optional[str], optional
        :return: The constructed SQL data structure request.
        :rtype: List[Dict[str, str]]
        """
        
        if system_context is None:
            system_context = self.prompts._openai_sql_data_structure_prompt
        
        message = [
            {"role": "system", "content": system_context},
            {"role": "user", "content": f'Context: {user_context}\n\nQuestion": {user_question}\n\nAnswer: {user_answer}'},
        ]

        return message

    def _openai_sql_request_structure(
        self, 
        user_context: str,
        user_question: str,
        system_context: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """Constructs a SQL request structure for OpenAI's API.

        :param user_context: The context of the SQL query.
        :type user_context: str
        :param user_question: The question of the SQL query.
        :type user_question: str
        :param system_context: The context of the SQL query, None results in class default
        :type system_context: Optional[str], optional
        :return: The constructed SQL request structure.
        :rtype: List[Dict[str, str]]
        """
        
        if system_context is None:
            system_context = self.prompts._openai_sql_request_structure_prompt
        
        message = [
            {"role": "system", "content": system_context},
            {"role": "user", "content": f'Context: {user_context}\n\nQuestion": {user_question}'},
        ]

        return message
    
    def openai_sql_response(
        self, 
        response_object: OpenAIObject,
    ) -> Optional[str]: 
        """Parses the response from OpenAI's API.
        
        :param response_object: The response from OpenAI's API.
        :type response_object: OpenAIObject
        :return: The parsed response.
        :rtype: Optional[str]
        """

        try:
            response = response_object.choices[0].message
        except Exception as e:
            logger.warning(f"OpenAI response failed to parse with error: {e}")
            return None

        if len(response.keys()) > 2: 
            logger.warning(f"OpenAI response has more than 2 keys: {response.keys()}")

        try: 
            sqlglot.parse(response["content"])
        except Exception as e:
            logger.warning(f"SQL query failed to parse with error: {e}")
            return None

        return response["content"]

    def openai_sql_request(
        self, 
        user_context: str,
        user_question: str,
        model: Optional[str] = "gpt-3.5-turbo", # TODO: consider using an enum for this
        system_context: Optional[str] = None,
        validate_response: Optional[bool] = False,
    ) -> Optional[OpenAIObject]:
        """Constructs a prompt to request a SQL query from OpenAI's API.
        
        :param user_context: The context of the SQL query.
        :type user_context: str
        :param user_question: The question of the SQL query.
        :type user_question: str
        :param model: The model to use for the request, defaults to "gpt-3.5-turbo"
        :type model: Optional[str], optional
        :param system_context: The context of the SQL query, None results in class default
        :type system_context: Optional[str], optional
        :param validate_response: Whether to validate the response, defaults to True. Returns None if validation fails.
        :type validate_response: Optional[bool], optional
        :return: The constructed SQL request.
        :rtype: OpenAIObject
        """

        message = self._openai_sql_request_structure(user_context, user_question, system_context)

        try: 
            request = self.openai.ChatCompletion.create(
                model=model, 
                messages=message,
            )
        except Exception as e:
            logger.warning(f"OpenAI request failed with error: {e}")
            raise e    

        if validate_response:
            return self.openai_sql_response(request)

        return request
    
    def openai_dataset_request(
        self, 
        dataset: Dataset,
        #context_label: Optional[str] = "context",
        #question_label: Optional[str] = "question",
    ): 
        
        context = dataset['context']
        question = dataset['question']
        inference = self.openai_sql_request(user_context=context, user_question=question)

        return {"openai_inference": inference}
    


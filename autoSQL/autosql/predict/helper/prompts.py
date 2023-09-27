class Prompts: 
    """This is simply a class for storing prompt text. 
    """

    def __init__(self) -> None:
        
        self._openai_sql_data_structure_prompt = "Given the Context (SQL Tables), the Question, and the Answer (SQL Query), create filler data that will return a value in the format of: '{table: [column: value, ...]}'"
        self._openai_sql_request_structure_prompt = "Context contains the relevant SQL tables, provide the query that answers the Question in response."

        self.rates = {
            "gpt-3.5-turbo": {
                "input_token_rate": 0.003 / 1000,
                "output_token_rate": 0.04 / 1000
            },
        }
    
    
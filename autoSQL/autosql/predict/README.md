Here's a concise `README` for the `SQLPredict` class within the `predict` folder:

---

# SQLPredict

## Overview

The `SQLPredict` class facilitates the dispatching of inference requests to various models. It primarily interacts with the OpenAI and Replicate APIs.

## Setup

1. **Dependencies**:
   - openai
   - replicate
   - sqlglot
   - datasets

2. **API Keys**:
   Ensure you have valid OpenAI and Replicate API keys for initializing the `SQLPredict` class.

## Usage

### Initialization

- **Direct Initialization**:
  ```python
  predictor = SQLPredict(openai_api_key="YOUR_OPENAI_KEY", replicate_api_key="YOUR_REPLICATE_KEY")
  ```

- **Initialization with a Replicate model**:
  ```python
  predictor = SQLPredict.from_replicate_model(openai_api_key="YOUR_OPENAI_KEY", replicate_api_key="YOUR_REPLICATE_KEY", model_name="MODEL_NAME", model_id="MODEL_ID")
  ```

### Adding Models

To add a Replicate model:
```python
predictor.add_replicate_model(model_name="MODEL_NAME", model_id="MODEL_ID")
```

### Request Construction

- **OpenAI SQL Data Structure**:
  Use `_openai_sql_data_structure()` to construct a SQL data structure request for OpenAI's API.

- **OpenAI SQL Request Structure**:
  Use `_openai_sql_request_structure()` to construct a SQL request structure for OpenAI's API.

### Sending Requests

- **OpenAI SQL Request**:
  Use `openai_sql_request()` to send a SQL request to OpenAI's API.

- **OpenAI Dataset Request**:
  Use `openai_dataset_request()` to send a dataset item request to OpenAI's API.

- **Replicate SQL Request**:
  Use `replicate_sql_request()` to send a SQL request to Replicate's API.

- **Replicate Dataset Request**:
  Use `replicate_dataset_request()` to send a dataset item request to Replicate's API.

### Parsing Responses

- **OpenAI SQL Response**:
  Use `openai_sql_response()` to parse the response from OpenAI's API.

## Logging

Any failures or issues during request creation, sending, or response parsing are logged as warnings.

## Inferences

| Date     | Avg. Inference Time (1/100) | Model             | Data                                                   | 
|----------|-----------------------------|-------------------|--------------------------------------------------------|
| 09/27/23 | 1.80s/request               | `gpt-3.5-turbo`   | [rich_testing_subset][rich_testing_subset] (0, 100)    |
| 09/27/23 | 1.54s/request               | `gpt-3.5-turbo`   | [rich_testing_subset][rich_testing_subset] (100, 200)  |
| 09/27/23 | 1.38s/request               | `gpt-3.5-turbo`   | [rich_testing_subset][rich_testing_subset] (200, 300)  |
| 09/27/23 | 3.08s/request               | `llama-2-13b-sql` | [rich_testing_subset][rich_testing_subset] (0, 100)    |
| 09/27/23 | 2.45s/request               | `llama-2-13b-sql` | [rich_testing_subset][rich_testing_subset] (100, 200)  |
| 09/27/23 | 1.38s/request               | `llama-2-13b-sql` | [rich_testing_subset][rich_testing_subset] (200, 300)  |

[gpt-3.5-turbo]: 
[llama-2-13b-sql]: 
[rich_testing_subset]: https://huggingface.co/datasets/alagaesia/auto-sql-create-context/blob/main/rich_testing_subset_llama_13b_1_0_0_inferences.zip
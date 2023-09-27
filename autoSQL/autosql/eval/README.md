# SQLEval

SQLEval is a Python utility that evaluates the performance of model inferences on SQL datasets.

## Overview

SQLEval provides functionality to:

1. Validate SQL queries against given datasets.
2. Check the accuracy of inference results against expected results.
3. Parse SQL queries from textual inferences.

Key features:
- Supports both OpenAI and Replicate models.
- Utilizes the SQLglot library for SQL query execution and error handling.
- Provides clear feedback on SQL validation and parsing errors.

## Usage

See `eval.ipynb` for an example of how to use SQLEval.

## Dependencies
- `re`
- `json`
- `datasets`
- `sqlglot`
# SQLData

## Overview

The `SQLData` class is a utility class designed to facilitate the handling and processing of SQL data, particularly datasets from sources like [b-mc2/sql-create-context](https://huggingface.co/datasets/b-mc2/sql-create-context). It serves as a tool to expand the feature set of your data, validate queries, generate test data, and filter rows based on various criteria. This helps in mitigating issues related to type comparison, as described in [this article](https://www.anyscale.com/blog/fine-tuning-llama-2-a-comprehensive-case-study-for-tailoring-models-to-unique-applications?s=03), and fixing minor syntax errors in your data.

### Initializing the SQLData Class

You can initiate the SQLData class as follows:

```python 
from autosql.data import SQLData
sd = SQLData()

# Optionally, only store a subset of the data in the class for testing purposes
dataset_name = "b-mc2/sql-create-context" # Expects a dataset from the Hugging Face Hub
sd = SQLData().from_dataset(dataset_name = dataset_name, subset = True, subset_value = 1000)
```

### Loading Data

The data can be loaded from a dataset or imported from a local file:

```python
# Loading data from a dataset
dataset_name = 'b-mc2/sql-create-context' # Expects a dataset from the Hugging Face Hub
sd = SQLData.from_dataset(dataset_name=dataset_name, subset=True, subset_value=100)

# Importing data from a local pickle file
dataset = pickle.load(open('test_sql_data.pkl', 'rb')) # Expects a dataset.DatasetDict
sd.import_data(dataset=dataset, dataset_name='test_dataset')
```

### Processing Data

Preprocessing allows you to enhance the data by adding features, validating queries, and more:

```python
sd.preprocess_data(
    dataset_name='test_dataset', 
    blanket_answer_syntax=True, 
    compute_table_count=True, 
    abstract_column_types=True,
    identify_duplicate_create_table=True,
    populate_data=True,
    validate_query=True,
    update_class_dataset=True,       
)
```

### Filtering Data

Filtering allows you to: 1) drop any invalid `answers` from the dataset, 2) drop any invalid `context` values from the dataset, 3) drop any `answers` with `sample_data` that result in empty query responses. Optionally, you can either return the dataset or update the instance stored within the class instance. 

```python
test_set = sd.filter_data(
    dataset_name='test_dataset', 
    drop_invalid_query=True,
    drop_duplicate_tables=True,
    drop_empty_query_result=False,
    update_class_dataset=True
)
```

## Understanding AST

An AST is a tree representation of the syntactic structure of source code in programming languages. Each node of the tree denotes a construct occurring in the source code. In the context of SQL, it would represent the structure of a SQL query.

Now let's delve into the AST structure for SQL:

1. **Root Node**:
   - The root node represents the entire SQL statement.

2. **Statement Nodes**:
   - These nodes represent individual SQL statements such as `CREATE`, `SELECT`, `INSERT`, `UPDATE`, or `DELETE`. Depending on your AST structure, this might be at the root level or a level below it.

3. **Clause Nodes**:
   - These nodes represent various clauses in SQL statements such as `WHERE`, `FROM`, `GROUP BY`, `ORDER BY`, and `HAVING`.

4. **Expression Nodes**:
   - These nodes represent expressions which can be arithmetic operations, comparisons, function calls, etc.

5. **Literal Nodes**:
   - These nodes represent literals such as strings, numbers, booleans, etc.

6. **Identifier Nodes**:
   - These nodes represent identifiers like column names, table names, aliases, etc.

Here's a simple visualization of an AST structure for a basic SQL query (`SELECT age FROM users WHERE age > 25`):

```plaintext
            [ROOT]
              |
          [SELECT]
           /    \
       [FROM]  [WHERE]
        /         \
    [USERS]     [EXPRESSION]
                   /      \
               [AGE]   [LITERAL: 25]
                   \
                 [OPERATOR: >]
```

In this tree:

- **[ROOT]**: Represents the entire query.
- **[SELECT]**: Represents the SELECT statement.
- **[FROM]**: Represents the FROM clause, with "users" as the table name.
- **[WHERE]**: Represents the WHERE clause.
- **[EXPRESSION]**: Represents the comparison expression.
- **[AGE]**: Represents the column name involved in the comparison.
- **[LITERAL: 25]**: Represents the value being compared against.
- **[OPERATOR: >]**: Represents the comparison operator.


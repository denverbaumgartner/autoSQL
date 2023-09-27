# autoSQL
A repo focused on the efficient use of LLMs for generating SQL code from natural language prompts. Details regarding the `SQLData` class can be found [here](https://github.com/denverbaumgartner/autoSQL/tree/main/autoSQL/autosql/data). Details regarding tuning can be found [here](https://github.com/denverbaumgartner/autoSQL/tree/main/autoSQL/autosql/tuning). Details regarding `SQLPredict` class can be found [here](https://github.com/denverbaumgartner/autoSQL/blob/main/autoSQL/autosql/predict/README.md). Details regarding the `SQLEval` class can be found [here](https://github.com/denverbaumgartner/autoSQL/blob/main/autoSQL/autosql/eval/README.md), and it is recommended that users read the `eval.ipynb` notebook for a quick tutorial on how to use the `SQLEval` class.

### Directory 

```
.
├── LICENSE
├── README.md
└── autosql
    ├── README.md
    ├── autosql
    │   ├── __init__.py
    │   ├── data
    │   │   ├── README.md
    │   │   ├── __init__.py
    │   │   ├── data.py
    │   │   └── helpers
    │   │       ├── __init__.py
    │   │       ├── generate.py
    │   │       └── upload.py
    │   ├── eval
    │   │   ├── README.md
    │   │   ├── __init__.py
    │   │   ├── eval.ipynb
    │   │   └── eval.py
    │   ├── example_pipeline.ipynb
    │   ├── predict
    │   │   ├── README.md
    │   │   ├── __init__.py
    │   │   ├── helper
    │   │   │   ├── __init__.py
    │   │   │   └── prompts.py
    │   │   └── predict.py
    │   └── tuning
    │       ├── README.md
    │       ├── __init__.py
    │       └── tune.py
    ├── poetry.lock
    ├── pyproject.toml
    └── tests
        ├── __init__.py
        ├── auto_sql_test.py
        └── test_sql_data.pkl
```

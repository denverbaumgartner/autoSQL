import json
import pickle
from autosql.data import SQLData


class TestSQLData:
    def test_class_creation(self):
        # Test base class creation
        sd = SQLData()
        assert isinstance(sd, SQLData)

        # Test creation from a valid dataset (Requires Internet Connection)
        dataset_name = "b-mc2/sql-create-context"
        sd = SQLData.from_dataset(dataset_name=dataset_name)
        assert isinstance(sd, SQLData)
        assert len(sd.data[dataset_name]["train"]) == 78577

        # Test creation with a sample size
        sd = SQLData.from_dataset(
            dataset_name=dataset_name, subset=True, subset_value=100
        )
        assert isinstance(sd, SQLData)
        assert len(sd.data[dataset_name]["train"]) == 100

    def test_data_loading(self):
        sd = SQLData()
        dataset = pickle.load(open("test_sql_data.pkl", "rb"))
        sd.import_data(dataset=dataset, dataset_name="test_dataset")
        assert isinstance(sd, SQLData)
        assert len(sd.data["test_dataset"]["train"]) == 100

    def test_data_generator(self):
        # Test base class creation
        sd = SQLData()
        assert isinstance(sd, SQLData)

        # Test generate_random_data types
        assert isinstance(
            sd.data_generator.generate_random_data(data_type="VARCHAR"), str
        )
        assert isinstance(sd.data_generator.generate_random_data(data_type="INT"), int)

        # Test generate_filler_data
        columns = {"table_name": {"column_var": "VARCHAR", "column_int": "INT"}}
        filler_data = sd.data_generator.generate_filler_data(
            column_types=columns, num_records=1
        )
        assert list(filler_data.keys()) == ["table_name"]
        assert list(filler_data["table_name"][0].keys()) == ["column_var", "column_int"]
        assert isinstance(filler_data["table_name"][0]["column_var"], str)
        assert isinstance(filler_data["table_name"][0]["column_int"], int)

    def test_data_transformations(self):
        sd = SQLData()
        dataset = pickle.load(open("test_sql_data.pkl", "rb"))
        sd.import_data(dataset=dataset, dataset_name="test_dataset")

        # Test _blanket_answer_syntax
        test_set = sd.preprocess_data(
            dataset_name="test_dataset",
            blanket_answer_syntax=True,
            compute_table_count=False,
            abstract_column_types=False,
            identify_duplicate_create_table=False,
            populate_data=False,
            validate_query=False,
            update_class_dataset=False,
        )
        assert (
            test_set["train"][80]["answer"]
            == "SELECT T1.name, T1.id FROM station AS T1 JOIN status AS T2 ON T1.id = T2.station_id GROUP BY T2.station_id HAVING AVG(T2.bikes_available) > 14 UNION SELECT name, id FROM station WHERE installation_date LIKE '12/%'"
        )

        # Test _compute_table_count
        test_set = sd.preprocess_data(
            dataset_name="test_dataset",
            blanket_answer_syntax=False,
            compute_table_count=True,
            abstract_column_types=False,
            identify_duplicate_create_table=False,
            populate_data=False,
            validate_query=False,
            update_class_dataset=False,
        )
        assert test_set["train"][80]["table_count"] == 3

        # Test _abstract_column_types
        test_set = sd.preprocess_data(
            dataset_name="test_dataset",
            blanket_answer_syntax=False,
            compute_table_count=False,
            abstract_column_types=True,
            identify_duplicate_create_table=False,
            populate_data=False,
            validate_query=False,
            update_class_dataset=False,
        )
        assert (
            test_set["train"][80]["column_types"]
            == '{"station": {"name": "VARCHAR", "id": "VARCHAR", "installation_date": "VARCHAR"}, "status": {"station_id": "VARCHAR", "bikes_available": "INT"}}'
        )

        # Test _identify_duplicate_create_table
        test_set = sd.preprocess_data(
            dataset_name="test_dataset",
            blanket_answer_syntax=False,
            compute_table_count=True,
            abstract_column_types=True,
            identify_duplicate_create_table=True,
            populate_data=False,
            validate_query=False,
            update_class_dataset=False,
        )
        assert test_set["train"][80]["duplicate_create_table"] == True

        # Test _populate_data
        test_set = sd.preprocess_data(
            dataset_name="test_dataset",
            blanket_answer_syntax=False,
            compute_table_count=True,
            abstract_column_types=True,
            identify_duplicate_create_table=True,
            populate_data=True,
            validate_query=False,
            update_class_dataset=False,
        )
        assert list(json.loads(test_set["train"][80]["filler_data"]).keys()) == [
            "station",
            "status",
        ]

        # Test validate_query without _blanket_answer_syntax
        test_set = sd.preprocess_data(
            dataset_name="test_dataset",
            blanket_answer_syntax=False,
            compute_table_count=True,
            abstract_column_types=True,
            identify_duplicate_create_table=True,
            populate_data=True,
            validate_query=True,
            update_class_dataset=False,
        )
        assert test_set["train"][80]["valid_query"] == False

        # Test validate_query with _blanket_answer_syntax
        test_set = sd.preprocess_data(
            dataset_name="test_dataset",
            blanket_answer_syntax=True,
            compute_table_count=True,
            abstract_column_types=True,
            identify_duplicate_create_table=True,
            populate_data=True,
            validate_query=True,
            update_class_dataset=False,
        )
        assert test_set["train"][80]["valid_query"] == True

        # Test update_class_dataset
        test_set = sd.preprocess_data(
            dataset_name="test_dataset",
            blanket_answer_syntax=True,
            compute_table_count=True,
            abstract_column_types=True,
            identify_duplicate_create_table=True,
            populate_data=True,
            validate_query=True,
            update_class_dataset=True,
        )
        assert test_set == None
        assert sd.data["test_dataset"]["train"][0]["valid_query"] == True

    def test_data_filters(self):
        sd = SQLData()
        dataset = pickle.load(open("test_sql_data.pkl", "rb"))
        sd.import_data(dataset=dataset, dataset_name="test_dataset")

        # Preprocess data
        sd.preprocess_data(
            dataset_name="test_dataset",
            blanket_answer_syntax=True,
            compute_table_count=True,
            abstract_column_types=True,
            identify_duplicate_create_table=True,
            populate_data=True,
            validate_query=True,
            update_class_dataset=True,
        )

        # Test drop_invalid_query filter
        test_set = sd.filter_data(
            dataset_name="test_dataset",
            drop_invalid_query=True,
            drop_duplicate_tables=False,
            drop_empty_query_result=False,
            update_class_dataset=False,
        )
        assert len(test_set["train"]) == 95

        # Test drop_duplicate_tables filter
        test_set = sd.filter_data(
            dataset_name="test_dataset",
            drop_invalid_query=False,
            drop_duplicate_tables=True,
            drop_empty_query_result=False,
            update_class_dataset=False,
        )
        assert len(test_set["train"]) == 98

        # Test drop_empty_query_result filter
        test_set = sd.filter_data(
            dataset_name="test_dataset",
            drop_invalid_query=False,
            drop_duplicate_tables=False,
            drop_empty_query_result=True,
            update_class_dataset=False,
        )
        for i in range(
            len(test_set["train"])
        ):  # since we are randomly generating data using names, this answer should never be true. if we improve our data generation, we should update this test
            assert (
                test_set["train"][i]["answer"]
                != "SELECT DISTINCT T1.creation FROM department AS T1 JOIN management AS T2 ON T1.department_id = T2.department_id JOIN head AS T3 ON T2.head_id = T3.head_id WHERE T3.born_state = 'Alabama'"
            )

        # Test update_class_dataset with filter drop_invalid_query
        test_set = sd.filter_data(
            dataset_name="test_dataset",
            drop_invalid_query=True,
            drop_duplicate_tables=False,
            drop_empty_query_result=False,
            update_class_dataset=True,
        )
        assert test_set == None
        assert sd.data["test_dataset"]["train"].num_rows == 95

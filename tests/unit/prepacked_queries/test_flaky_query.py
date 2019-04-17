"""
Tests for the Flaky query.
"""
from unittest.mock import MagicMock, patch
from elasticsearch_dsl import Search

from ebr_connector.prepacked_queries.flaky_jobs import get_flaky_tests
from . import get_batch_data, get_results_data_for_ids, get_num_passes_data_for_test


def mock_search(index=None):
    mock_search_result = MagicMock()
    mock_search_result.source = MagicMock()
    return Search()

def mock_source(includes=None, excludes=None):
    return Search()

def mock_metric(name, agg_type, *args, **params):
    return Search()


@patch("ebr_connector.schema.build_results.BuildResults.search", side_effect=mock_search)
@patch("elasticsearch_dsl.aggs.AggBase.metric", side_effect=mock_metric)
@patch("elasticsearch_dsl.Search.source", side_effect=mock_source)
@patch("elasticsearch_dsl.Search.execute")
def test_flaky_query(
        mock_execute,
        mock_metric,
        mock_source,
        mock_search):
    """Tests that `get_flaky_tests` returns the correct flaky test analysis data.
    """
    # Given
    # Mock the responses from the Elasticsearch executions
    mock_execute.side_effect = [
        get_batch_data(),
        get_results_data_for_ids(["id1", "id2", "id3", "id4"]),
        get_num_passes_data_for_test("class1", "test1", ["id1", "id2", "id3", "id4"]),
        get_num_passes_data_for_test("class1", "test2", ["id1", "id2", "id3", "id4"]),
        get_num_passes_data_for_test("class1", "test3", ["id1", "id2", "id3", "id4"]),
        get_results_data_for_ids(["id5", "id6"]),
        get_num_passes_data_for_test("class1", "test2", ["id5", "id6"]),
        get_num_passes_data_for_test("class1", "test3", ["id5", "id6"]),
        get_results_data_for_ids(["id8"]),
        get_num_passes_data_for_test("class1", "test1", ["id8"]),
        get_num_passes_data_for_test("class1", "test2", ["id8"]),
        get_num_passes_data_for_test("class1", "test3", ["id8"]),
        get_num_passes_data_for_test("class1", "test4", ["id8"]),
        get_results_data_for_ids(["id9", "id10"]),
        get_results_data_for_ids(["id11", "id12"]),
        get_num_passes_data_for_test("class1", "test3", ["id11", "id12"])
    ]

    def verify_data(actual_data, expected_data):
        for key in expected_data:
            assert actual_data[key] == expected_data[key]

    # When
    flaky_tests = get_flaky_tests(index="my_index", start_date="now-4w", end_date="now")

    # Then
    assert len(flaky_tests) == 1
    assert "class1" in flaky_tests
    assert len(flaky_tests["class1"]) == 3
    assert "test1" in flaky_tests["class1"]
    assert "test2" in flaky_tests["class1"]
    assert "test3" in flaky_tests["class1"]

    assert len(flaky_tests["class1"]["test2"]) == 1
    assert len(flaky_tests["class1"]["test2"][0]["builds"]) == 2

    verify_data(flaky_tests["class1"]["test1"][0], {
        "class_name": "class1",
        "test_name": "test1",
        "platform": "platform1",
        "product_version": "productversion1",
        "report_set": "reportset1",
        "build_version": "buildversion1",
        "job_name": "jobname1",
        "num_failures": 2,
        "num_passes": 1,
        "num_runs": 3,
        "num_skipped": 0,
        "flaky_score": 100 * 2 / 3
    })

    verify_data(flaky_tests["class1"]["test2"][0]["builds"][0], {
        "build_date_time": "2019-04-16T22:03:45",
        "build_id": "buildid1"
    })

    verify_data(flaky_tests["class1"]["test2"][0]["builds"][1], {
        "build_date_time": "2019-04-16T22:03:46",
        "build_id": "buildid2"
    })

    assert len(flaky_tests["class1"]["test3"]) == 3
    assert len(flaky_tests["class1"]["test3"][0]["builds"]) == 3
    assert len(flaky_tests["class1"]["test3"][1]["builds"]) == 2

    verify_data(flaky_tests["class1"]["test3"][0], {
        "class_name": "class1",
        "test_name": "test3",
        "platform": "platform1",
        "product_version": "productversion1",
        "report_set": "reportset1",
        "build_version": "buildversion1",
        "job_name": "jobname1",
        "num_failures": 1,
        "num_passes": 1,
        "num_runs": 3,
        "num_skipped": 1,
        "flaky_score": 100
    })

    verify_data(flaky_tests["class1"]["test3"][0]["builds"][0], {
        "build_date_time": "2019-04-16T22:03:42",
        "build_id": "buildid1"
    })

    verify_data(flaky_tests["class1"]["test3"][0]["builds"][1], {
        "build_date_time": "2019-04-16T22:03:43",
        "build_id": "buildid2"
    })

    verify_data(flaky_tests["class1"]["test3"][0]["builds"][2], {
        "build_date_time": "2019-04-16T22:03:44",
        "build_id": "buildid3"
    })

    verify_data(flaky_tests["class1"]["test3"][1], {
        "class_name": "class1",
        "test_name": "test3",
        "platform": "platform2",
        "product_version": "productversion1",
        "report_set": "reportset1",
        "build_version": "buildversion1",
        "job_name": "jobname1",
        "num_failures": 1,
        "num_passes": 1,
        "num_runs": 2,
        "num_skipped": 0,
        "flaky_score": 100
    })

    verify_data(flaky_tests["class1"]["test3"][1]["builds"][0], {
        "build_date_time": "2019-04-16T22:03:45",
        "build_id": "buildid1"
    })

    verify_data(flaky_tests["class1"]["test3"][1]["builds"][1], {
        "build_date_time": "2019-04-16T22:03:46",
        "build_id": "buildid2"
    })

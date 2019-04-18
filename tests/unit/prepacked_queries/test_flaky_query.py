"""
Tests for the Flaky query.
"""
from unittest.mock import patch
from elasticsearch_dsl import Search

from ebr_connector.prepacked_queries.flaky_jobs import get_flaky_tests
from . import get_batch_data, get_results_data_for_ids, get_num_passes_data_for_test


def mock_buildresults_search(index=None):
    """Mocks the BuildResults search() function.
    """
    # pylint: disable=unused-argument
    return Search()

def mock_esdsl_metric(name, agg_type, *args, **params):
    """Mocks the Elasticsearch DSL metric() function.
    """
    # pylint: disable=unused-argument
    return Search()

def mock_esdsl_source(includes=None, excludes=None):
    """Mocks the Elasticsearch DSL source() function.
    """
    # pylint: disable=unused-argument
    return Search()


@patch("ebr_connector.schema.build_results.BuildResults.search", side_effect=mock_buildresults_search)
@patch("elasticsearch_dsl.aggs.AggBase.metric", side_effect=mock_esdsl_metric)
@patch("elasticsearch_dsl.Search.source", side_effect=mock_esdsl_source)
@patch("elasticsearch_dsl.Search.execute")
def test_flaky_query(
        mock_execute,
        mock_source,
        mock_metric,
        mock_search):
    """Tests that `get_flaky_tests` returns the correct flaky test analysis data.
    """
    # pylint: disable=unused-argument
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
    # Validate we find expected flaky tests "class1.test1", "class1.test2" and "class1.test3"
    assert len(flaky_tests) == 1
    assert "class1" in flaky_tests
    assert len(flaky_tests["class1"]) == 3
    assert "test1" in flaky_tests["class1"]
    assert "test2" in flaky_tests["class1"]
    assert "test3" in flaky_tests["class1"]

    # Validate test "class1.test1"
    assert len(flaky_tests["class1"]["test1"]) == 1
    assert len(flaky_tests["class1"]["test1"][0]["builds"]) == 3

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

    verify_data(flaky_tests["class1"]["test1"][0]["builds"][0], {
        "build_date_time": "2019-04-16T22:03:42",
        "build_id": "buildid1"
    })

    verify_data(flaky_tests["class1"]["test1"][0]["builds"][1], {
        "build_date_time": "2019-04-16T22:03:43",
        "build_id": "buildid2"
    })

    verify_data(flaky_tests["class1"]["test1"][0]["builds"][2], {
        "build_date_time": "2019-04-16T22:03:44",
        "build_id": "buildid3"
    })

    # Validate test "class1.test2"
    assert len(flaky_tests["class1"]["test2"]) == 1
    assert len(flaky_tests["class1"]["test2"][0]["builds"]) == 2

    verify_data(flaky_tests["class1"]["test2"][0], {
        "class_name": "class1",
        "test_name": "test2",
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

    verify_data(flaky_tests["class1"]["test2"][0]["builds"][0], {
        "build_date_time": "2019-04-16T22:03:45",
        "build_id": "buildid1"
    })

    verify_data(flaky_tests["class1"]["test2"][0]["builds"][1], {
        "build_date_time": "2019-04-16T22:03:46",
        "build_id": "buildid2"
    })

    # Validate test "class1.test3"
    assert len(flaky_tests["class1"]["test3"]) == 3
    assert len(flaky_tests["class1"]["test3"][0]["builds"]) == 3
    assert len(flaky_tests["class1"]["test3"][1]["builds"]) == 2
    assert len(flaky_tests["class1"]["test3"][2]["builds"]) == 2

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

    verify_data(flaky_tests["class1"]["test3"][2], {
        "class_name": "class1",
        "test_name": "test3",
        "platform": "platform1",
        "product_version": "productversion1",
        "report_set": "reportset1",
        "build_version": "buildversion2",
        "job_name": "jobname1",
        "num_failures": 1,
        "num_passes": 1,
        "num_runs": 2,
        "num_skipped": 0,
        "flaky_score": 100
    })

    verify_data(flaky_tests["class1"]["test3"][2]["builds"][0], {
        "build_date_time": "2019-04-16T22:03:51",
        "build_id": "buildid1"
    })

    verify_data(flaky_tests["class1"]["test3"][2]["builds"][1], {
        "build_date_time": "2019-04-16T22:03:52",
        "build_id": "buildid2"
    })

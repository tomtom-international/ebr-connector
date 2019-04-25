"""
Tests for the Failing query.
"""
from unittest.mock import MagicMock, patch
from elasticsearch_dsl import Search

from ebr_connector.prepacked_queries.test_results import get_failing_tests
from . import get_results_data_for_ids

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
def test_flaky_query(mock_execute, mock_source, mock_metric, mock_search):

    mock_execute.side_effect = [
            get_results_data_for_ids(["id1", "id4", "id5", "id6", "id8", "id9", "id10", "id11", "id12"])
    ]

    def verify_data(actual_data, expected_data):
        for key in expected_data:
            assert actual_data[key] == expected_data[key]
            
    failing_tests = get_failing_tests(index="my_index", start_date="now-1w", end_date="now")

    assert len(failing_tests) == 22

    verify_data(failing_tests[0], {
         'status': 'FAILED', 
         'collector': None, 
         'build_id': 'buildid1', 
         'product': None, 
         'platform': 'platform1', 
         'job_name': 'jobname1', 
         'build_date': '2019-04-16T22:03:41', 
         'build_version': 'buildversion1', 
         'product_version': 'productversion1', 
         'test_name': 'test1', 
         'class_name': 'class1', 
         'error_message': None, 
         'duration': None, 
         'report_set': 'reportset1'
    })

    assert failing_tests[0]['test_name'] == 'test1'
    assert failing_tests[1]['test_name'] == 'test2'
    assert failing_tests[2]['test_name'] == 'test1'
    assert failing_tests[3]['test_name'] == 'test2'
    assert failing_tests[4]['test_name'] == 'test3'
    assert failing_tests[5]['test_name'] == 'test1'
    assert failing_tests[6]['test_name'] == 'test1'
    assert failing_tests[7]['test_name'] == 'test2'
    assert failing_tests[8]['test_name'] == 'test3'
    assert failing_tests[9]['test_name'] == 'test1'
    assert failing_tests[10]['test_name'] == 'test2'
    assert failing_tests[11]['test_name'] == 'test3'
    assert failing_tests[12]['test_name'] == 'test4'
    assert failing_tests[13]['test_name'] == 'test1'
    assert failing_tests[14]['test_name'] == 'test2'
    assert failing_tests[15]['test_name'] == 'test1'
    assert failing_tests[16]['test_name'] == 'test2'
    assert failing_tests[17]['test_name'] == 'test1'
    assert failing_tests[18]['test_name'] == 'test2'
    assert failing_tests[19]['test_name'] == 'test1'
    assert failing_tests[20]['test_name'] == 'test2'
    assert failing_tests[21]['test_name'] == 'test3'

    print("FAILING TESTS FROM TESTS: %s" % (failing_tests))
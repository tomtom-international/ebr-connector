"""
Tests for the examples.
"""

from ebr_connector.examples.query import query_failed_tests, query_for_successful_job
from .conftest import get_index_name


# pylint: disable=unused-argument
def test_query_failed_tests(data_client):
    """Test `query_failed_tests` example.
    """
    response = query_failed_tests(get_index_name())
    assert len(response) == 1 # 1 documents
    assert len(response[0]["br_tests_object"]["br_tests_failed_object"]) == 5

# pylint: disable=unused-argument
def test_query_for_successful_job(data_client):
    """Test `query_for_successful_job` example.
    """
    response = query_for_successful_job(get_index_name())
    assert len(response) == 1
    assert not "br_tests_failed_object" in response[0]["br_tests_object"]
    assert not "br_tests_skipped_object" in response[0]["br_tests_object"]
    assert len(response[0]["br_tests_object"]["br_tests_passed_object"]) == 15

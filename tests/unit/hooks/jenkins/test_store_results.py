"""
Tests for the Jenkins hook.
"""

from unittest.mock import MagicMock, patch
from json.decoder import JSONDecodeError

from ebr_connector.hooks.jenkins.store_results import store
from . import get_jenkins_test_report_response


@patch("socket.socket")
@patch("ssl.create_default_context")
@patch("ebr_connector.hooks.common.store_results.get_json_job_details")
def test_store_tests_returns_valid_build_results_document(
        mock_get_json_job_details,
        mock_ssl_create_default_context,
        mock_socket):
    """Tests that `store_tests` translates the test data object properly to a BuildResults document.
    """
    # Given
    mock_socket = mock_socket.return_value
    mock_context = MagicMock()
    mock_ssl_create_default_context.return_value = mock_context

    ## Mocked arguments
    mock_args = MagicMock()
    mock_args.buildurl = "abc"
    mock_args.buildid = "123"
    mock_args.platform = "platform"
    mock_args.productversion = "1234abc"

    ## Mock the JSON response from Jenkins REST APIs
    mock_get_json_job_details.side_effect = [
        {"fullName": "a_job_name"},
        {"url": "http://abc", "timestamp": "1550567699000", "result": "FAILURE"},
        get_jenkins_test_report_response()]

    # When
    build_results = store(mock_args)

    # Then
    assert len(build_results.br_tests_object.br_tests_failed_object) == 2
    assert len(build_results.br_tests_object.br_tests_passed_object) == 13
    assert len(build_results.br_tests_object.br_tests_skipped_object) == 1

    assert build_results.br_tests_object.br_summary_object.br_total_failed_count == 2
    assert build_results.br_tests_object.br_summary_object.br_total_passed_count == 13
    assert build_results.br_tests_object.br_summary_object.br_total_skipped_count == 1
    assert build_results.br_tests_object.br_summary_object.br_total_count == 16

    assert len(build_results.br_tests_object.br_suites_object) == 4


@patch("socket.socket")
@patch("ssl.create_default_context")
@patch("ebr_connector.hooks.common.store_results.get_json_job_details")
def test_store_tests_should_return_empty_results_if_json_decoder_exception_thrown(
        mock_get_json_job_details,
        mock_ssl_create_default_context,
        mock_socket):
    """Tests that `store_tests` translates the test data object properly to a BuildResults document.
    """
    # Given
    mock_socket = mock_socket.return_value
    mock_context = MagicMock()
    mock_ssl_create_default_context.return_value = mock_context

    ## Mocked arguments
    mock_args = MagicMock()
    mock_args.buildurl = "abc"
    mock_args.buildid = "123"
    mock_args.platform = "platform"
    mock_args.productversion = "1234abc"

    ## Mock the JSON response from Jenkins REST APIs
    mock_get_json_job_details.side_effect = [
        {"fullName": "a_job_name"},
        {"url": "http://abc", "timestamp": "1550567699000", "result": "FAILURE"},
        JSONDecodeError("dummy message", "doc", 1)]

    # When
    build_results = store(mock_args)

    # Then
    assert not build_results.br_tests_object.br_tests_failed_object
    assert not build_results.br_tests_object.br_tests_passed_object
    assert not build_results.br_tests_object.br_tests_skipped_object

    assert not build_results.br_tests_object.br_summary_object.br_total_failed_count
    assert not build_results.br_tests_object.br_summary_object.br_total_passed_count
    assert not build_results.br_tests_object.br_summary_object.br_total_skipped_count
    assert not build_results.br_tests_object.br_summary_object.br_total_count

    assert not build_results.br_tests_object.br_suites_object

"""
Tests for the BuildResults module.
"""

from datetime import datetime
from unittest.mock import ANY, call, MagicMock, patch
import socket
import json
import ssl
import pytest

import ebr_connector
from ebr_connector.schema.build_results import BuildResults
from tests import get_test_data_for_failed_build


@pytest.mark.parametrize("test_input,expected", [
    ("Success", BuildResults.BuildStatus.SUCCESS),

    ("Failure", BuildResults.BuildStatus.FAILURE),
    ("Failed", BuildResults.BuildStatus.FAILURE),

    ("Abort", BuildResults.BuildStatus.ABORTED),
    ("Aborted", BuildResults.BuildStatus.ABORTED),
    ("Cancel", BuildResults.BuildStatus.ABORTED),
    ("Cancelled", BuildResults.BuildStatus.ABORTED),

    ("Not_built", BuildResults.BuildStatus.NOT_BUILT),
    ("Skipped", BuildResults.BuildStatus.NOT_BUILT),

    ("Unstable", BuildResults.BuildStatus.UNSTABLE),

    ("Timeout", BuildResults.BuildStatus.TIMEOUT),
    ("Timedout", BuildResults.BuildStatus.TIMEOUT),

    ("Running", BuildResults.BuildStatus.RUNNING),
    ("Building", BuildResults.BuildStatus.RUNNING),
])
def test_create_valid_status(test_input, expected):
    """Test various valid build status strings that can be converted
    to proper :class:`ebr_connector.schema.BuildResults` objects.
    """
    assert BuildResults.BuildStatus.create(test_input) == expected
    assert BuildResults.BuildStatus.create(test_input.lower()) == expected
    assert BuildResults.BuildStatus.create(test_input.upper()) == expected


def test_create_status_throws_exception():
    """Test that unknown status strings should result in exception.
    """
    with pytest.raises(ValueError):
        BuildResults.BuildStatus.create("unknown_status")


def test_default_constructor():
    """Test default constructor
    """
    build_results = BuildResults()
    assert build_results.__dict__ == {"_d_": {}, "meta": {}}


def test_create_factory_method():
    """Test create factory method
    """
    date_time = datetime.utcnow()
    build_results = BuildResults.create(job_name="my_jobname", job_link="my_joburl",
                                        build_date_time=str(date_time), build_id="1234",
                                        platform="Linux-x86_64", product="MyProduct")

    assert build_results.br_job_name == "my_jobname"
    assert build_results.br_job_url_key == "my_joburl"
    assert build_results.br_build_date_time == str(date_time)
    assert build_results.br_build_id_key == "1234"
    assert build_results.br_platform == "Linux-x86_64"
    assert build_results.br_product == "MyProduct"
    assert build_results.br_version_key == ebr_connector.__version__

    assert build_results.to_dict() == {
        "br_build_date_time": str(date_time),
        "br_build_id_key": "1234",
        "br_job_name": "my_jobname",
        "br_job_url_key": "my_joburl",
        "br_platform": "Linux-x86_64",
        "br_product": "MyProduct",
        "br_version_key": ebr_connector.__version__
        }


def create_dummy_build_result():
    """Creates a dummy build results object
    """

    date_time = datetime.utcnow()
    return BuildResults.create(job_name="my_jobname", job_link="my_joburl",
                               build_date_time=str(date_time), build_id="1234",
                               platform="Linux-x86_64", product="MyProduct")


def test_store_tests_with_empty_tests_and_suites():
    """Test with no tests and suites.
    """
    # Given
    build_results = create_dummy_build_result()

    retrieve_mock = MagicMock()
    retrieve_mock.return_value = {
        "tests": [],
        "suites": []
    }

    # When
    build_results.store_tests(retrieve_mock)

    # Then
    assert build_results.br_tests_object == {"br_tests_passed_object": [], "br_tests_failed_object": [], "br_tests_skipped_object": [],
                                             "br_summary_object": {"br_total_count": 0, "br_total_failed_count": 0,
                                                                   "br_total_passed_count": 0, "br_total_skipped_count": 0}}


def test_store_tests_with_empty_results():
    """Test with no tests and suites.
    """
    # Given
    build_results = create_dummy_build_result()

    retrieve_mock = MagicMock()
    retrieve_mock.return_value = {}

    # When
    build_results.store_tests(retrieve_mock)

    # Then
    assert build_results.br_tests_object == {}


@patch("socket.socket")
@patch("ssl.create_default_context")
@pytest.mark.parametrize("cafile_input", [
    (None),
    ("my_cacert.pem")
])
def test_save_logcollect(
        mock_ssl_create_default_context,
        mock_socket_class,
        cafile_input):
    """Test checking that sockets are properly created and data send to server.
    """
    # Given
    ## bare socket
    mock_socket = mock_socket_class.return_value
    mock_context = MagicMock()
    ## SSL context
    mock_ssl_create_default_context.return_value = mock_context

    ## build results under test with some test data
    build_results = create_dummy_build_result()
    build_results.store_tests(get_test_data_for_failed_build)

    # When
    build_results.save_logcollect(dest="localhost", port="10000", cafile=cafile_input)

    # Then
    ## Constructor call
    mock_socket_class.assert_has_calls([
        call(socket.AF_INET, socket.SOCK_STREAM)
    ])
    ## Instance calls
    mock_socket.settimeout.assert_called_with(10)

    mock_ssl_create_default_context.assert_called_with(cafile=cafile_input)
    expected_calls = [
        call.wrap_socket(mock_socket, server_hostname="localhost"),
        call.wrap_socket().__enter__(),
        call.wrap_socket().__enter__().connect(("localhost", "10000")),
        call.wrap_socket().__enter__().send(str.encode(json.dumps(build_results.to_dict())))
    ]
    mock_context.assert_has_calls(expected_calls)


#@patch("socket.socket")
@patch("ssl.create_default_context")
def test_save_logcollect_should_use_client_authentication(
        mock_ssl_create_default_context):
    """Test that connection is established with client authentication
    """
    # Given
    mock_context = MagicMock()
    ## SSL context
    mock_ssl_create_default_context.return_value = mock_context

    ## build results under test with some test data
    build_results = create_dummy_build_result()
    build_results.store_tests(get_test_data_for_failed_build)

    # When
    build_results.save_logcollect(dest="localhost", port="10000", clientcert="myclientcert")

    # Then
    assert mock_context.verify_mode == ssl.CERT_REQUIRED
    mock_context.assert_has_calls([
        call.load_cert_chain("myclientcert", ANY, ANY)
    ])


def test_store_tests_returns_a_properly_translated_document():
    """Tests that `store_tests` translates the test data object properly to a BuildResults document.
    """
    # Given
    build_results = create_dummy_build_result()

    # When
    build_results.store_tests(get_test_data_for_failed_build)

    # Then
    assert len(build_results.br_tests_object.br_tests_failed_object) == 5
    assert len(build_results.br_tests_object.br_tests_passed_object) == 5
    assert len(build_results.br_tests_object.br_tests_skipped_object) == 5

    assert build_results.br_tests_object.br_summary_object.br_total_failed_count == 5
    assert build_results.br_tests_object.br_summary_object.br_total_passed_count == 5
    assert build_results.br_tests_object.br_summary_object.br_total_skipped_count == 5
    assert build_results.br_tests_object.br_summary_object.br_total_count == 15

    assert len(build_results.br_tests_object.br_suites_object) == 5
    for suite in build_results.br_tests_object.br_suites_object:
        assert suite.br_failures_count == 1
        assert suite.br_passed_count == 1
        assert suite.br_skipped_count == 1
        assert suite.br_total_count == 3


@pytest.mark.parametrize("exception", [
    KeyError("dummy key error"),
    TypeError("dummy type error")
])
def test_store_status_should_not_throw(exception):
    """`store_status` should not throw the above mentioned exceptions
    but instead catch them internally.
    """
    # Given
    build_results = create_dummy_build_result()
    mock_status_callback = MagicMock()
    mock_status_callback.side_effect = exception

    # When & Then
    try:
        build_results.store_status(mock_status_callback)
    except type(exception) as err:
        pytest.fail("Thrown %s is not expected!" % err.__class__)


def test_store_status_called_without_args():
    """Tests that `store_status` calls the callback function without args.
    """
    # Given
    build_results = create_dummy_build_result()
    mock_status_callback = MagicMock()

    # When
    build_results.store_status(mock_status_callback)

    # Then
    mock_status_callback.assert_called_once_with()


@pytest.mark.parametrize("args_input,args_expected", [
    ("{'id': 'test'}", "{'id': 'test'}"),
    ("test", "test")
])
def test_store_status_called_with_args(
        args_input,
        args_expected):
    """Tests that `store_status` calls the callback function with args.
    """
    # Given
    build_results = create_dummy_build_result()
    mock_status_callback = MagicMock()

    # When
    build_results.store_status(mock_status_callback, args_input)

    # Then
    mock_status_callback.assert_called_once_with(args_expected)

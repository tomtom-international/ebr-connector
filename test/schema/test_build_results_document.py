"""
Tests for the BuildResults module.
"""

from datetime import datetime
from unittest.mock import MagicMock
import pytest

import elastic
from elastic.schema.build_results import BuildResults


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
    to proper :class:`elastic.schema.BuildResults` objects.
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
    assert build_results.__dict__ == {'_d_': {}, 'meta': {}}


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
    assert build_results.br_version_key == elastic.__version__

    assert build_results.to_dict() == {
        'br_build_date_time': str(date_time),
        'br_build_id_key': '1234',
        'br_job_name': 'my_jobname',
        'br_job_url_key': 'my_joburl',
        'br_platform': 'Linux-x86_64',
        'br_product': 'MyProduct',
        'br_version_key': elastic.__version__
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

    build_results = create_dummy_build_result()

    retrieve_mock = MagicMock()
    retrieve_mock.return_value = {
        'tests': [],
        'suites': []
    }

    build_results.store_tests(retrieve_mock)

    assert build_results.br_tests_object == {'br_tests_passed_object': [], 'br_tests_failed_object': [], 'br_tests_skipped_object': [],
                                             'br_summary_object': {'br_total_count': 0, 'br_total_failed_count': 0,
                                                                   'br_total_passed_count': 0, 'br_total_skipped_count': 0}}

def test_store_tests_with_empty_results():
    """Test with no tests and suites.
    """

    build_results = create_dummy_build_result()

    retrieve_mock = MagicMock()
    retrieve_mock.return_value = {}

    build_results.store_tests(retrieve_mock)

    assert build_results.br_tests_object == {}

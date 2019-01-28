"""
Tests for the BuildResults module.
"""

from datetime import datetime
import pytest

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
    assert build_results.meta == {}


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

"""
Tests for the Test innerdoc class.
"""

import pytest

from elastic.schema.build_results import Test


@pytest.mark.parametrize("test_input,expected", [
    ("Success", Test.Result.PASSED),
    ("Fixed", Test.Result.PASSED),
    ("Pass", Test.Result.PASSED),
    ("Passed", Test.Result.PASSED),

    ("Failure", Test.Result.FAILED),
    ("Error", Test.Result.FAILED),
    ("Regression", Test.Result.FAILED),
    ("Failed", Test.Result.FAILED),

    ("Skip", Test.Result.SKIPPED),
    ("Skipped", Test.Result.SKIPPED),
])
def test_create_valid_test_result(test_input, expected):
    """Test various valid test result strings that can be converted
    to proper :class:`elastic.schema.Test.Result` objects.
    """
    assert Test.Result.create(test_input) == expected
    assert Test.Result.create(test_input.lower()) == expected
    assert Test.Result.create(test_input.upper()) == expected


def test_create_test_result_throws_exception():
    """Test that unknown status strings should result in exception.
    """
    with pytest.raises(ValueError):
        Test.Result.create("unknown_result")


def test_default_ctor():
    """Test default constructor
    """
    test = Test()
    assert test.meta == {}


def test_create_factory_method():
    """Test create factory method
    """
    test = Test.create(suite="my_suitename", classname="***REMOVED***",
                       result="SUCCESS", message="my_message", duration=100.12, reportset="my_unittests")
    assert test.br_suite == "my_suitename"
    assert test.br_classname == "my_classname"
    assert test.br_test == "my_testname"
    assert test.br_result == "SUCCESS"
    assert test.br_message == "my_message"
    assert test.br_duration == 100.12
    assert test.br_reportset == "my_unittests"

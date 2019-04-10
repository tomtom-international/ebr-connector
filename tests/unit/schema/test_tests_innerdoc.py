"""
Tests for the Tests innerdoc class.
"""

from unittest.mock import Mock
from ebr_connector.schema.build_results import Tests

def test_default_ctor():
    """Test default constructor
    """
    summary = Tests()
    assert summary.__dict__ == {'_d_': {}, 'meta': {}}


def test_create_factory_method():
    """TestSummary create factory method
    """
    summary = Mock()
    suites = Mock()
    tests_passed = Mock()
    tests_failed = Mock()
    tests_skipped = Mock()

    tests = Tests.create(suites=suites, tests_passed=tests_passed, tests_failed=tests_failed, tests_skipped=tests_skipped, summary=summary)
    assert tests.br_suites_object == suites
    assert tests.br_summary_object == summary
    assert tests.br_tests_failed_object == tests_failed
    assert tests.br_tests_passed_object == tests_passed
    assert tests.br_tests_skipped_object == tests_skipped

"""
Tests for the TestSuite innerdoc class.
"""


from ebr_connector.schema.build_results import TestSuite


def test_default_ctor():
    """TestSuite default constructor
    """
    test_suite = TestSuite()
    assert test_suite.__dict__ == {'_d_': {}, 'meta': {}}


def test_create():
    """Test create factory method
    """
    test_suite = TestSuite.create(name="my_suitename", failures_count=10, skipped_count=2, passed_count=20, total_count=32, duration=30.5)
    assert test_suite.br_name == "my_suitename"
    assert test_suite.br_failures_count == 10
    assert test_suite.br_skipped_count == 2
    assert test_suite.br_passed_count == 20
    assert test_suite.br_total_count == 32
    assert test_suite.br_duration == 30.5

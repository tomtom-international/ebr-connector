"""
Tests for the TestSuite innerdoc class.
"""


from elastic.schema.build_results import TestSuite


def test_default_ctor():
    """TestSuite default constructor
    """
    test = TestSuite()
    assert test.meta == {}


def test_create():
    """Test create factory method
    """
    test = TestSuite.create(name="my_suitename", failures_count=10, skipped_count=2, passed_count=20, total_count=32, duration=30.5)
    assert test.br_name == "my_suitename"
    assert test.br_failures_count == 10
    assert test.br_skipped_count == 2
    assert test.br_passed_count == 20
    assert test.br_total_count == 32
    assert test.br_duration == 30.5

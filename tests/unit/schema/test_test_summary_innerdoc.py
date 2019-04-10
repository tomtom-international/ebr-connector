"""
Tests for the TestSummary innerdoc class.
"""

from ebr_connector.schema.build_results import TestSummary

def test_default_ctor():
    """Test default constructor
    """
    summary = TestSummary()
    assert summary.__dict__ == {'_d_': {}, 'meta': {}}


def test_create_factory_method():
    """TestSummary create factory method
    """
    test_summary = TestSummary.create(total_passed_count=10, total_failed_count=2, total_skipped_count=3, total_count=15)
    assert test_summary.br_total_passed_count == 10
    assert test_summary.br_total_failed_count == 2
    assert test_summary.br_total_skipped_count == 3
    assert test_summary.br_total_count == 15

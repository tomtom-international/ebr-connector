"""
Tests for the QuickBuild StoreResults module.
"""

from unittest.mock import MagicMock

import elastic.hooks.quickbuild.store_results as store_results
from elastic.schema.build_results import BuildResults, Test
from qb_results_exporter.qb_results_exporter import QBResultsExporter


DUMMY_BUILD_INFO_SUCCESS = {
    QBResultsExporter.KEY_BUILD_ID: '123456',
    QBResultsExporter.KEY_BUILD_STATUS: 'SUCCESS'
}

DUMMY_BUILD_INFO_FAILURE = {
    QBResultsExporter.KEY_BUILD_ID: '654321',
    QBResultsExporter.KEY_BUILD_STATUS: 'FAILURE'
}

DUMMY_REPORT_SETS = [
    'Report Set 1',
    'Report Set 2'
]

DUMMY_BUILD_TEST_DATA_SUCCESS = {
    'Report Set 1': [
        {
            QBResultsExporter.KEY_TEST_NAME: 'Test 1',
            QBResultsExporter.KEY_CLASS_NAME: 'Class 1',
            QBResultsExporter.KEY_DURATION: 123,
            QBResultsExporter.KEY_PACKAGE_NAME: 'Package 1',
            QBResultsExporter.KEY_STATUS: 'PASSED',
            QBResultsExporter.KEY_ERROR_MESSAGE: None,
            QBResultsExporter.KEY_REPORT_SET: 'Report Set 1'
        },
        {
            QBResultsExporter.KEY_TEST_NAME: 'Test 2',
            QBResultsExporter.KEY_CLASS_NAME: 'Class 2',
            QBResultsExporter.KEY_DURATION: 456,
            QBResultsExporter.KEY_PACKAGE_NAME: 'Package 2',
            QBResultsExporter.KEY_STATUS: 'PASSED',
            QBResultsExporter.KEY_ERROR_MESSAGE: None,
            QBResultsExporter.KEY_REPORT_SET: 'Report Set 1'
        }
    ],
    'Report Set 2': [
        {
            QBResultsExporter.KEY_TEST_NAME: 'Test 3',
            QBResultsExporter.KEY_CLASS_NAME: 'Class 1',
            QBResultsExporter.KEY_DURATION: 321,
            QBResultsExporter.KEY_PACKAGE_NAME: 'Package 1',
            QBResultsExporter.KEY_STATUS: 'PASSED',
            QBResultsExporter.KEY_ERROR_MESSAGE: None,
            QBResultsExporter.KEY_REPORT_SET: 'Report Set 2'
        }
    ]
}

DUMMY_BUILD_TEST_DATA_FAILURE = {
    'Report Set 1': [
        {
            QBResultsExporter.KEY_TEST_NAME: 'Test 1',
            QBResultsExporter.KEY_CLASS_NAME: 'Class 1',
            QBResultsExporter.KEY_DURATION: 123,
            QBResultsExporter.KEY_PACKAGE_NAME: 'Package 1',
            QBResultsExporter.KEY_STATUS: 'PASSED',
            QBResultsExporter.KEY_ERROR_MESSAGE: None,
            QBResultsExporter.KEY_REPORT_SET: 'Report Set 1'
        },
        {
            QBResultsExporter.KEY_TEST_NAME: 'Test 2',
            QBResultsExporter.KEY_CLASS_NAME: 'Class 2',
            QBResultsExporter.KEY_DURATION: 456,
            QBResultsExporter.KEY_PACKAGE_NAME: 'Package 2',
            QBResultsExporter.KEY_STATUS: 'FAILED',
            QBResultsExporter.KEY_ERROR_MESSAGE: 'Error 3',
            QBResultsExporter.KEY_REPORT_SET: 'Report Set 1'
        }
    ],
    'Report Set 2': [
        {
            QBResultsExporter.KEY_TEST_NAME: 'Test 3',
            QBResultsExporter.KEY_CLASS_NAME: 'Class 1',
            QBResultsExporter.KEY_DURATION: 321,
            QBResultsExporter.KEY_PACKAGE_NAME: 'Package 1',
            QBResultsExporter.KEY_STATUS: 'SKIPPED',
            QBResultsExporter.KEY_ERROR_MESSAGE: None,
            QBResultsExporter.KEY_REPORT_SET: 'Report Set 2'
        }
    ]
}


class MockedQBResultsExporter():
    """
    Mocked QBResultsExporter object.
    """
    def __init__(self, logger=None, qb_username=None, qb_password=None):
        self.logger = logger
        self.qb_username = qb_username
        self.qb_password = qb_password
        self.build_test_data = None
        self.build_id = None
        self.report_sets = None

    def set_build_test_data(self, build_test_data):
        """Set build test data.
        """
        self.build_test_data = build_test_data

    def get_build_test_data(self, build_id, report_sets):
        """Get previously set build test data and set the given build ID.
        """
        self.build_id = build_id
        self.report_sets = report_sets
        return self.build_test_data

    def get_build_id(self):
        """Get build ID.
        """
        return self.build_id

    def get_report_sets(self):
        """Get report sets.
        """
        return self.report_sets


def verify_test(test, test_name, suite_name, class_name, result, message, duration, reportset):
    """Verify that test object has expected field values.
    """
    assert test['suite'] == suite_name
    assert test['classname'] == class_name
    assert test['test'] == test_name
    assert test['result'] == result.name
    assert test['message'] == message
    assert test['duration'] == duration
    assert test['reportset'] == reportset

def verify_suite(suite, suite_name, passed_count, failures_count, skipped_count, duration, package):
    """Verify that suite object has expected field values.
    """
    assert suite['failures_count'] == failures_count
    assert suite['skipped_count'] == skipped_count
    assert suite['passed_count'] == passed_count
    assert suite['name'] == suite_name
    assert suite['total_count'] == failures_count + skipped_count + passed_count
    assert suite['duration'] == duration
    assert suite['package'] == package

def verify_results_success(results):
    """Verify that success results list has expected tests and suites.
    """
    tests = results['tests']
    assert len(tests) == 3
    verify_test(tests[0], 'Test 1', 'Class 1', 'Class 1', Test.Result.PASSED, None, 123, 'Report Set 1')
    verify_test(tests[1], 'Test 2', 'Class 2', 'Class 2', Test.Result.PASSED, None, 456, 'Report Set 1')
    verify_test(tests[2], 'Test 3', 'Class 1', 'Class 1', Test.Result.PASSED, None, 321, 'Report Set 2')

    suites = results['suites']
    assert len(suites) == 2
    verify_suite(suites[0], 'Class 1', 2, 0, 0, 123 + 321, 'Package 1')
    verify_suite(suites[1], 'Class 2', 1, 0, 0, 456, 'Package 2')

def verify_results_failure(results):
    """Verify that failure results list has expected tests and suites.
    """
    tests = results['tests']
    assert len(tests) == 3
    verify_test(tests[0], 'Test 1', 'Class 1', 'Class 1', Test.Result.PASSED, None, 123, 'Report Set 1')
    verify_test(tests[1], 'Test 2', 'Class 2', 'Class 2', Test.Result.FAILED, 'Error 3', 456, 'Report Set 1')
    verify_test(tests[2], 'Test 3', 'Class 1', 'Class 1', Test.Result.SKIPPED, None, 321, 'Report Set 2')

    suites = results['suites']
    assert len(suites) == 2
    verify_suite(suites[0], 'Class 1', 1, 0, 1, 123 + 321, 'Package 1')
    verify_suite(suites[1], 'Class 2', 0, 1, 0, 456, 'Package 2')

def test_format_quickbuild_results_success():
    """Test that passing QuickBuild test data is correctly formatted.
    """
    results, build_status = store_results.format_quickbuild_results(DUMMY_BUILD_TEST_DATA_SUCCESS)
    assert build_status == BuildResults.BuildStatus.SUCCESS
    verify_results_success(results)

def test_format_quickbuild_results_failure():
    """Test that failing QuickBuild test data is correctly formatted.
    """
    results, build_status = store_results.format_quickbuild_results(DUMMY_BUILD_TEST_DATA_FAILURE)
    assert build_status == BuildResults.BuildStatus.FAILURE
    verify_results_failure(results)

def test_quickbuild_xml_decode_success():
    """Test that passing QuickBuild test data is correctly exported.
    """
    mock_logger = MagicMock()
    qb_results_exporter = MockedQBResultsExporter()
    qb_results_exporter.set_build_test_data(DUMMY_BUILD_TEST_DATA_SUCCESS)
    results = store_results.quickbuild_xml_decode(DUMMY_BUILD_INFO_SUCCESS, DUMMY_REPORT_SETS,
                                                  qb_results_exporter, mock_logger)
    verify_results_success(results)
    assert qb_results_exporter.get_build_id() == '123456'
    assert qb_results_exporter.get_report_sets() == DUMMY_REPORT_SETS

def test_quickbuild_xml_decode_failure():
    """Test that failing QuickBuild test data is correctly exported.
    """
    mock_logger = MagicMock()
    qb_results_exporter = MockedQBResultsExporter()
    qb_results_exporter.set_build_test_data(DUMMY_BUILD_TEST_DATA_FAILURE)
    results = store_results.quickbuild_xml_decode(DUMMY_BUILD_INFO_FAILURE, DUMMY_REPORT_SETS,
                                                  qb_results_exporter, mock_logger)
    verify_results_failure(results)
    assert qb_results_exporter.get_build_id() == '654321'
    assert qb_results_exporter.get_report_sets() == DUMMY_REPORT_SETS

def test_get_status():
    """Test that correct status is returned.
    """
    status = store_results.get_status(DUMMY_BUILD_INFO_SUCCESS)
    assert status == BuildResults.BuildStatus.SUCCESS.name

    status = store_results.get_status(DUMMY_BUILD_INFO_FAILURE)
    assert status == BuildResults.BuildStatus.FAILURE.name

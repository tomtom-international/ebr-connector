# -*- coding: utf-8 -*-

"""Module providing some test data.
"""

from ebr_connector.schema.build_results import Test


def get_test_data_for_successful_build():
    """Returns a test data set of test suites and cases that passed.
    """
    return _get_test_data(["PASSED", "PASSED", "PASSED"])


def get_test_data_for_failed_build():
    """Returns a test data set of test suites and cases with some failed/passed/skipped tests.
    """
    return _get_test_data(["SKIPPED", "FAILED", "PASSED"])


def _get_test_data(test_case_results):
    """Returns suites with `len(test_case_results)` test cases per suite.
    """
    results = {
        'tests': [],
        'suites': []
    }

    for suite_index in range(0, 5):
        failed_case_no = 0
        passed_case_no = 0
        skipped_case_no = 0
        suite_duration = 0
        suite_name = "MySuite_%s" % str(suite_index)

        for test_index, result in enumerate(test_case_results):
            test_result = Test.Result.create(result)
            test = {
                'suite': suite_name,
                'classname': "org.acme.MyTest_%s_%s" % (str(suite_index), str(test_index)),
                'test': "test_case_%s" % str(test_index),
                'result': test_result.name,
                'message': "Some test output message - %s" % str(test_index),
                'duration': float(158 + suite_index + test_index)
            }

            if test_result == Test.Result.FAILED:
                failed_case_no += 1
            elif test_result == Test.Result.SKIPPED:
                skipped_case_no += 1
            else:
                passed_case_no += 1
            suite_duration += test['duration']
            results['tests'].append(test)

        suite_result = {
            'failures_count': failed_case_no,
            'skipped_count': skipped_case_no,
            'passed_count': passed_case_no,
            'total_count': len(test_case_results),
            'name': suite_name,
            'duration': suite_duration
        }

        results['suites'].append(suite_result)

    return results

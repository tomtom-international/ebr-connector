# -*- coding: utf-8 -*-

"""Module providing some test data.
"""

from elastic.schema.build_results import Test

def get_test_data():
    """Returns a test data set of test suites and cases.
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

        test_cases = ["SKIPPED", "FAILED", "PASSED"]
        for test_index, result in enumerate(test_cases):
            test_result = Test.Result.create(result)
            test = {
                'suite': suite_name,
                'classname': "org.acme.MyTest_%s_%s" % (str(suite_index), str(test_index)),
                'test': "test_case_%s" % str(test_index),
                'result': test_result.name,
                'message': "Some test output message - %s" % str(test_index),
                'duration': float(2 + test_index)
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
            'total_count': len(test_cases),
            'name': suite_name,
            'duration': suite_duration
        }

        results['suites'].append(suite_result)

    return results

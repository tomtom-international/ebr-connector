#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Library for exporting Jenkins build results (including tests) to logstash
"""

import sys
from json.decoder import JSONDecodeError

import requests

from elastic.hooks.common.store_results import assemble_build, parse_args

def jenkins_json_decode(url):
    """
    Transforms the test results stored by Jenkins into the :class:`elastic.schema.BuildResults` format

    Args:
        url: URL to Jenkins build to record
    """
    results = {
        'tests': [],
        'suites': []
    }
    try:
        json_results = requests.get(url).json()
    except JSONDecodeError:
        print("Received error when parsing test results, no results will be included in build.")
        return results

    for suite in json_results['suites']:
        failed_case_no = 0
        passed_case_no = 0
        skipped_case_no = 0
        for case in suite['cases']:
            test = {
                'suite': suite['name'],
                'classname': case['className'],
                'test': case['name'],
                'result': case['status'],
                'message': case['errorDetails'],
                'duration': case['duration']
            }

            if case['status'] in ["FAILED", "REGRESSION"]:
                failed_case_no += 1
            elif case['status'] == "SKIPPED":
                skipped_case_no += 1
            else:
                passed_case_no += 1

            results['tests'].append(test)
        suite_result = {
            'failures_count': failed_case_no,
            'skipped_count': skipped_case_no,
            'passed_count': passed_case_no,
            'total_count': len(suite['cases']),
            'name': suite['name'],
            'duration': suite['duration']
        }

        results['suites'].append(suite_result)

    return results


def main():
    """
    Provides a CLI interface callable on Jenkins to send build results to logstash
    """
    args = parse_args("Send results of a Jenkins build to a LogCollector instance over TCP.")

    jenkins_build = assemble_build(args, jenkins_json_decode, [args.buildurl + "testReport/api/json"])

    jenkins_build.save_logcollect(args.logcollectaddr, args.logcollectport, cafile=args.cacert, clientcert=args.clientcert, clientkey=args.clientkey,
                                  keypass=args.clientpassword, timeout=args.sockettimeout)


if __name__ == '__main__':
    sys.exit(main())

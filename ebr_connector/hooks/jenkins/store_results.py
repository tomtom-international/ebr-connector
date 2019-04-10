#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Library for exporting Jenkins build results (including tests) to Elasticsearch
"""

import sys
from json.decoder import JSONDecodeError

import ebr_connector
from ebr_connector.hooks.common.store_results import assemble_build, parse_args, normalize_string
from ebr_connector.schema.build_results import Test


def jenkins_json_decode(url):
    """
    Transforms the test results stored by Jenkins into the :class:`ebr_connector.schema.BuildResults` format

    Args:
        url: URL to Jenkins build to record
    """
    results = {
        'tests': [],
        'suites': []
    }
    try:
        json_results = ebr_connector.hooks.common.store_results.get_json_job_details(url)
    except JSONDecodeError:
        print("Received error when parsing test results, no results will be included in build.")
        return results

    for suite in json_results['suites']:
        failed_case_no = 0
        passed_case_no = 0
        skipped_case_no = 0
        for case in suite['cases']:
            # Create Test.Result enum based on string
            test_result = Test.Result.create(normalize_string(case['status']))

            test = {
                'suite': normalize_string(suite['name']),
                'classname': normalize_string(case['className']),
                'test': normalize_string(case['name']),
                'result': test_result.name,
                'message': normalize_string(case['errorDetails']),
                'duration': float(case['duration'])
            }

            if test_result == Test.Result.FAILED:
                failed_case_no += 1
            elif test_result == Test.Result.SKIPPED:
                skipped_case_no += 1
            else:
                passed_case_no += 1

            results['tests'].append(test)
        suite_result = {
            'failures_count': failed_case_no,
            'skipped_count': skipped_case_no,
            'passed_count': passed_case_no,
            'total_count': len(suite['cases']),
            'name': normalize_string(suite['name']),
            'duration': float(suite['duration'])
        }

        results['suites'].append(suite_result)

    return results

def store(args):
    """Fetches the test report from Jenkins and stores the data into logstash.
    """
    jenkins_build = assemble_build(args, jenkins_json_decode, [args.buildurl + "/" + args.buildid + "/testReport/api/json"])
    jenkins_build.save_logcollect(args.logcollectaddr, args.logcollectport, cafile=args.cacert, clientcert=args.clientcert, clientkey=args.clientkey,
                                  keypass=args.clientpassword, timeout=args.sockettimeout)
    return jenkins_build


def main():
    """
    Provides a CLI interface callable on Jenkins to send build results to Elasticsearch.
    """
    args = parse_args("Send results of a Jenkins build to a LogCollector instance over TCP.")
    store(args)


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from json.decoder import JSONDecodeError
import argparse

import requests


from elastic.schema.build_results import BuildResults
from elastic.hooks.common.args import add_common_args


def status(args):
    return args.buildstatus


def jenkins_json_decode(url):
    results = {
        'tests': [],
        'suites': []
    }
    try:
        json_results = requests.get(url).json()
    except JSONDecodeError:
        print("Recieved error when parsing test results, no results will be included in build.")
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
            'failuresCount': failed_case_no,
            'skippedCount': skipped_case_no,
            'passedCount': passed_case_no,
            'totalCount': len(suite['cases']),
            'name': suite['name'],
            'duration': suite['duration']
        }

        results['suites'].append(suite_result)

    return results


def main():
    parser = argparse.ArgumentParser(
        description='Send results of a Jenkins build to a LogCollector instance over TCP.')
    parser.add_argument(
        '--buildurl',
        required=True,
        help='URL of build to send')
    parser.add_argument(
        '--buildtime',
        required=True,
        help="Build date-time string")
    parser.add_argument(
        '--buildstatus',
        required=True,
        help="Build status string")
    add_common_args(parser)
    args = parser.parse_args()

    if (args.clientcert or args.clientkey) and not (
            args.clientcert and args.clientkey):
        print("Either both '--clientcert' and '--clientkey' must be set or neither should be set.")
        exit()

    jenkins_build = BuildResults(
        jobName=args.jobname,
        buildId=args.buildid,
        buildDateTime=args.buildtime,
        jobLink=args.buildurl)
    jenkins_build.store_tests(
        jenkins_json_decode,
        args.buildurl +
        "testReport/api/json")
    jenkins_build.store_status(status, args)

    jenkins_build.save(
        args.logcollectaddr,
        args.logcollectport,
        cafile=args.cacert,
        clientcert=args.clientcert,
        clientkey=args.clientkey,
        keypass=args.clientpassword)


if __name__ == '__main__':
    sys.exit(main())

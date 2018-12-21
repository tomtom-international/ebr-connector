#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import requests
import sys

from datetime import datetime
from elastic.schema.BuildResults import BuildResults
from elastic.hooks.common.args import addCommonArgs
from json.decoder import JSONDecodeError


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
            'failures': failed_case_no,
            'skipped': skipped_case_no,
            'passed': passed_case_no,
            'total': len(suite['cases']),
            'name': suite['name'],
            'duration': suite['duration']
            }

        results['suites'].append(suite_result)

    return results


def main():
    parser = argparse.ArgumentParser(description='Send results of a Jenkins build to a LogCollector instance over TCP.')
    parser.add_argument('--buildurl', required=True, help='URL of build to send')
    parser.add_argument('--buildtime', required=True, help="Build date-time string")
    parser.add_argument('--buildstatus', required=True, help="Build status string")
    addCommonArgs(parser)
    args = parser.parse_args()

    if (args.clientcert or args.clientkey) and not (args.clientcert and args.clientkey):
        print("Either both '--clientcert' and '--clientkey' must be set or neither should be set.")
        exit()

    jenkinsBuild = BuildResults(jobName = args.jobname, buildId = args.buildid, buildDateTime = args.buildtime, jobLink = args.buildurl)
    jenkinsBuild.storeTests(jenkins_json_decode, args.buildurl + "testReport/api/json")
    jenkinsBuild.storeStatus(status, args)

    jenkinsBuild.save(args.logcollectaddr, args.logcollectport, cafile=args.cacert, clientcert=args.clientcert, clientkey=args.clientkey, keypass=args.clientpassword)


if __name__ == '__main__':
    sys.exit(main())

#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
Library pushing XUnit results to logstash. Intended as a baseline for any CI systems that do not provide XUnit file ingestion that can be used instead.
"""

import sys

from junitparser import JUnitXml

from elastic.hooks.common.store_results import assemble_build, parse_args
from elastic.schema.build_results import Test

def get_all_xunit_files(testfiles):
    """
    Takes a list of XUnit files and processes them into the :class:`elastic.schema.BuildResults` format

    Args:
        testfiles: A list of locations of XUnit XML files
    """
    results = {
        'tests': [],
        'suites': []
    }
    for testfile in testfiles:
        temp_results = get_xunit_results(testfile)
        results['tests'].extend(temp_results['tests'])
        results['suites'].extend(temp_results['suites'])
    return results

def get_xunit_results(filename):
    """
    Takes a single XUnit file and returns suites and tests in :class:`elastic.schema.BuildResults` format

    Args:
        testfile: the location of a single XUnit XML file
    """
    xml = JUnitXml.fromfile(filename)

    results = {
        'tests': [],
        'suites': []
    }

    for suite in xml:
        suite_result = {
            'failures_count': suite.failures + suite.errors,
            'skipped_count': suite.skipped,
            'passed_count': suite.tests - (suite.failures + suite.errors),
            'total_count': suite.tests,
            'name': suite.name,
            'duration': suite.time
        }
        results['suites'].append(suite_result)
        for case in suite:
            if case.result is None:
                result = Test.Result.create(case.result).name
                message = ""
            else:
                result = Test.Result.create(case.result.__class__.__name__).name
                message = case.result.message

            test = {
                'suite': suite.name,
                'classname': case.classname,
                'test': case.name,
                'result': result,
                'message': message,
                'duration': case.time
            }

            results['tests'].append(test)

    return results

def add_options(parser):
    """
    Adds the testfiles option to the arg parser object

    Args:
        parser: argparser object
    """
    parser.add_argument('--testfiles', nargs='+', required=True, help="List of XML files to parse")

def main():
    """
    Provides a CLI interface that takes in XUnit files and returns the results to logstash
    """
    args = parse_args("Send results of a Jenkins build to a LogCollector instance over TCP.", add_options)

    xunit_results = assemble_build(args, get_all_xunit_files, [args.testfiles])

    xunit_results.save_logcollect(args.logcollectaddr, args.logcollectport, cafile=args.cacert, clientcert=args.clientcert, clientkey=args.clientkey,
                                  keypass=args.clientpassword)

if __name__ == '__main__':
    sys.exit(main())

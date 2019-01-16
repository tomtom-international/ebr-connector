#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Library for exporting QuickBuild build results to logstash (ElasticSearch).
"""

import argparse
import getpass
import logging
import pprint
import sys

from qb_results_exporter.qb_results_exporter import QBResultsExporter
from elastic.schema.build_results import BuildResults, Test
from elastic.hooks.common.args import add_common_args, validate_args


DEFAULT_PROJECT_NAME = "NavKit"
DEFAULT_LOG_LEVEL = "INFO"


def parse_args(args=None):
    """
    Parses command line arguments.

    Args:
        args: Optional default arguments.

    Returns:
        Arguments object.
    """
    parser = argparse.ArgumentParser(description='Send results of a QuickBuild job to a LogCollector instance over TCP.')
    parser.add_argument("--product", type=str, default=DEFAULT_PROJECT_NAME, help="Product name (Default: %s)" % DEFAULT_PROJECT_NAME)
    parser.add_argument("--qbusername", dest="qb_username", help="Quickbuild username")
    parser.add_argument("--qbpassword", dest="qb_password", help="Quickbuild password")
    parser.add_argument("-l", "--log", action="store", type=str, dest="log_level", default=DEFAULT_LOG_LEVEL,
                        help="Log level (Default: %s)" % DEFAULT_LOG_LEVEL)
    add_common_args(parser)
    return parser.parse_args(args)


def log_formatted_results(logger, results):
    """
    Logs the results to be uploaded to logstash (for debugging purposes).

    Args:
        logger: Logger object.
        results: Results to be uploaded to logstash.
    """
    tests = results.get('tests', [])
    logger.debug("NUMBER OF FORMATTED TEST RESULTS: %d" % len(tests))
    logger.debug(
        "FAILING TESTS:\n" +
        pprint.pformat(
            list(
                filter(
                    lambda x: x['result'] in QBResultsExporter.QB_FAILURE_STATUSES,
                    tests))))

    suites = results.get('suites', [])
    logger.debug("NUMBER OF FORMATTED SUITE RESULTS: %d" % len(suites))
    logger.debug(
        "FAILING SUITES:\n" +
        pprint.pformat(
            list(
                filter(
                    lambda x: x['failures_count'] > 0,
                    suites))))


def format_quickbuild_results(build_test_data):
    """
    Converts the raw results from QuickBuild into a format used by logstash.

    Args:
        build_test_data: Test results data from QuickBuild for a particular build.

    Returns:
        logstash formatted results.
    """
    tests = []
    suites = {}

    for report_set in build_test_data:
        test_data = build_test_data[report_set]

        for test_details in test_data:
            suite = test_details[QBResultsExporter.KEY_CLASS_NAME]
            duration = test_details[QBResultsExporter.KEY_DURATION]
            package = test_details[QBResultsExporter.KEY_PACKAGE_NAME]

            # Create Test.Result enum based on string
            test_result = Test.Result.create(test_details[QBResultsExporter.KEY_STATUS])

            test = {
                'suite': suite,
                'classname': test_details[QBResultsExporter.KEY_CLASS_NAME],
                'test': test_details[QBResultsExporter.KEY_TEST_NAME],
                'result': test_result.name,
                'message': test_details[QBResultsExporter.KEY_ERROR_MESSAGE],
                'duration': duration,
                'reportset': test_details[QBResultsExporter.KEY_REPORT_SET]
            }

            tests.append(test)

            if suite not in suites:
                suites[suite] = {
                    'failures_count': 0,
                    'skipped_count': 0,
                    'passed_count': 0,
                    'name': suite,
                    'total_count': 0,
                    'duration': 0,
                    'package': None
                }

            suite_result = suites[suite]

            if package and not suite_result['package']:
                suite_result['package'] = package

            try:
                suite_result['duration'] += int(duration)
            except ValueError:
                pass

            suite_result['total_count'] += 1

            if test_result == Test.Result.PASSED:
                suite_result['passed_count'] += 1
            elif test_result == Test.Result.FAILED:
                suite_result['failures_count'] += 1
            else:
                suite_result['skipped_count'] += 1

    results = {
        'tests': tests,
        'suites': list(suites.values())
    }

    return results


def quickbuild_xml_decode(build_info, qb_results_exporter, logger):
    """
    Exports the raw results from QuickBuild for a particular build and formats them for use by logstash.

    Args:
        build_info: Dictionary containing information about the QuickBuild build.
        qb_results_exporter: QBResultsExporter object.
        logger: Logger object.

    Returns:
        logstash formatted results.
    """
    build_id = build_info.get(QBResultsExporter.KEY_BUILD_ID, None)

    build_test_data = qb_results_exporter.get_build_test_data(build_id)
    results = format_quickbuild_results(build_test_data)
    log_formatted_results(logger, results)
    return results

def status(build_info):
    """
    Returns the status of the QuickBuild build.

    Args:
        build_info: Dictionary containing information about the QuickBuild build.

    Returns:
        Status string of the QuickBuild build.
    """
    return BuildResults.BuildStatus.create(build_info.get(QBResultsExporter.KEY_BUILD_STATUS, None)).name


def main():
    """
    Exports QuickBuild build results to logstash.
    """
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logger = logging.getLogger('elastic.hook.quickbuild.store_results')

    args = parse_args()

    validate_args(args)

    if not args.qb_password and args.qb_username:
        args.qb_password = getpass.getpass(
            "Password for " + args.qb_username + ": ")

    logging.basicConfig(level=args.log_level.upper())
    qb_results_exporter = QBResultsExporter(
        logger, args.qb_username, args.qb_password)

    build_info = qb_results_exporter.get_build_info(args.buildid)
    build_date = build_info.get(
        QBResultsExporter.KEY_BUILD_DATE_TIME_UTC, None)
    build_url = build_info.get(QBResultsExporter.KEY_BUILD_URL, None)

    if build_date:
        build_date = build_date.isoformat()


    quick_build_results = BuildResults.create(platform=args.platform, job_name=args.jobname, build_id=args.buildid, build_date_time=build_date,
                                              job_link=build_url, product=args.product)
    quick_build_results.store_tests(quickbuild_xml_decode, build_info=build_info, qb_results_exporter=qb_results_exporter, logger=logger)
    quick_build_results.store_status(get_status, build_info=build_info)
    quick_build_results.save_logcollect(args.logcollectaddr, args.logcollectport, cafile=args.cacert, clientcert=args.clientcert,
                                        clientkey=args.clientkey, keypass=args.clientpassword, timeout=args.sockettimeout)


if __name__ == '__main__':
    sys.exit(main())

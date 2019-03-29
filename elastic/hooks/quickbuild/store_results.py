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
    parser.add_argument('--reportset', type=str, nargs='+', default=None, help='Report Set names. (Default: None, for all report sets)')
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
    logger.info("NUMBER OF FORMATTED TEST RESULTS: %d" % len(tests))
    logger.debug(
        "FAILING TESTS:\n" +
        pprint.pformat(
            list(
                "%s.%s" % (str(t['classname']), str(t['test'])) for t in filter(
                    lambda x: Test.Result.create(x['result']) == Test.Result.FAILED,
                    tests))))

    suites = results.get('suites', [])
    logger.info("NUMBER OF FORMATTED SUITE RESULTS: %d" % len(suites))
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
    build_status = None

    for report_set in build_test_data:
        test_data = build_test_data[report_set]

        for test_details in test_data:
            suite = test_details[QBResultsExporter.KEY_CLASS_NAME] or ""
            duration = test_details[QBResultsExporter.KEY_DURATION] or 0
            package = test_details[QBResultsExporter.KEY_PACKAGE_NAME] or ""

            try:
                duration = float(duration)
            except ValueError:
                duration = 0

            # Create Test.Result enum based on string
            test_result = Test.Result.create(test_details[QBResultsExporter.KEY_STATUS])

            test = {
                'suite': suite,
                'classname': suite,
                'test': test_details[QBResultsExporter.KEY_TEST_NAME],
                'result': test_result.name,
                'message': test_details[QBResultsExporter.KEY_ERROR_MESSAGE] or "",
                'duration': duration,
                'reportset': test_details[QBResultsExporter.KEY_REPORT_SET] or ""
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

            suite_result['duration'] += duration
            suite_result['total_count'] += 1

            if test_result == Test.Result.PASSED:
                suite_result['passed_count'] += 1
                if build_status is None:
                    build_status = BuildResults.BuildStatus.SUCCESS
            elif test_result == Test.Result.FAILED:
                suite_result['failures_count'] += 1
                build_status = BuildResults.BuildStatus.FAILURE
            else:
                suite_result['skipped_count'] += 1

    results = {
        'tests': tests,
        'suites': list(suites.values())
    }

    if not tests:
        raise ValueError("There are no test results in the QuickBuild data")

    return results, build_status


def quickbuild_xml_decode(build_info, report_sets, qb_results_exporter, logger):
    """
    Exports the raw results from QuickBuild for a particular build and formats them for use by logstash.

    Args:
        build_info: Dictionary containing information about the QuickBuild build.
        report_sets: List of report sets to get results from (or None for all report sets).
        qb_results_exporter: QBResultsExporter object.
        logger: Logger object.

    Returns:
        logstash formatted results.
    """
    build_id = build_info.get(QBResultsExporter.KEY_BUILD_ID, None)

    build_test_data = qb_results_exporter.get_build_test_data(build_id, report_sets)
    results, tests_build_status = format_quickbuild_results(build_test_data)
    build_status = BuildResults.BuildStatus.create(build_info.get(QBResultsExporter.KEY_BUILD_STATUS, None))

    # If the build is still running, we look at the test results to determine status
    if build_status == BuildResults.BuildStatus.RUNNING and tests_build_status is not None:
        build_info[QBResultsExporter.KEY_BUILD_STATUS] = tests_build_status.name

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


def main(args=None, qb_results_exporter_class=QBResultsExporter,
         build_results_class=BuildResults, getpass_class=getpass):
    """
    Exports QuickBuild build results to logstash.

    Args:
        qb_results_exporter_class: Optional QBResultsExporter class.
        build_results_class: Optional BuildResults class.
        getpass_class: Optional getpass class.
    """
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logger = logging.getLogger('elastic.hook.quickbuild.store_results')

    args = parse_args(args)

    validate_args(args)

    if not args.qb_password and args.qb_username:
        args.qb_password = getpass_class.getpass(
            "Password for " + args.qb_username + ": ")

    logging.basicConfig(level=args.log_level.upper())
    qb_results_exporter = qb_results_exporter_class(
        logger, args.qb_username, args.qb_password)

    build_info = qb_results_exporter.get_build_info(args.buildid)
    build_date = build_info.get(
        QBResultsExporter.KEY_BUILD_DATE_TIME_UTC, None)
    build_url = build_info.get(QBResultsExporter.KEY_BUILD_URL, None)
    build_version = build_info.get(QBResultsExporter.KEY_BUILD_VERSION, None)
    report_sets = args.reportset

    if build_date:
        build_date = build_date.isoformat()


    quick_build_results = build_results_class.create(platform=args.platform, job_name=args.jobname, build_id=args.buildid, build_date_time=build_date,
                                                     job_link=build_url, product=args.product, job_info=build_version, product_version=args.productversion)
    quick_build_results.store_tests(quickbuild_xml_decode, report_sets=report_sets, build_info=build_info, qb_results_exporter=qb_results_exporter, logger=logger)
    quick_build_results.store_status(get_status, build_info=build_info)
    quick_build_results.save_logcollect(args.logcollectaddr, args.logcollectport, cafile=args.cacert, clientcert=args.clientcert,
                                        clientkey=args.clientkey, keypass=args.clientpassword, timeout=args.sockettimeout)


if __name__ == '__main__':
    sys.exit(main())

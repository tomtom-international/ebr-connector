#!/usr/bin/python

import logging
import argparse
import pprint
from qb_results_exporter.qb_results_exporter import QBResultsExporter
from elastic.BuildResults import BuildResults


DEFAULT_PLATFORM_NAME = "linux"
DEFAULT_PROJECT_NAME = "NavKit"
DEFAULT_LOG_LEVEL = "INFO"


def add_args(parser):
    parser.add_argument("-b", "--build", dest="build_id", type=str, required=True, help="QuickBuild build ID")
    parser.add_argument("-j", "--jobname", dest="job_name", type=str, default=None, help="QuickBuild job name")
    parser.add_argument("-p", "--platform", dest="platform", type=str, default=DEFAULT_PLATFORM_NAME, help="Platform name (Default: %s)" % DEFAULT_PLATFORM_NAME)
    parser.add_argument("-s", "--stage", dest="stage", type=str, required=False, help="Stage name")
    parser.add_argument("--product", dest="product", type=str, default=DEFAULT_PROJECT_NAME, help="Product name (Default: %s)" % DEFAULT_PROJECT_NAME)
    parser.add_argument("--qbusername", dest="qb_username", help="Quickbuild username")
    parser.add_argument("--qbpassword", dest="qb_password", help="Quickbuild password")
    parser.add_argument("--logcollectaddr", dest="log_collect_addr", help="Address of LogCollector to send to")
    parser.add_argument("--logcollectport", dest="log_collect_port", help="Port on the LogCollector to send to", type=int)
    parser.add_argument("--cacert", default=None, help="Location of CA cert to verify against.")
    parser.add_argument("--clientcert", default=None, help="Client certificate file. Must also provide client key.")
    parser.add_argument("--clientkey", default=None, help="Client key file. Must also provide client certificate.")
    parser.add_argument("--clientpassword", default="", help="Client key file's password. Only use if there is a password on the keyfile.")
    parser.add_argument("-l", "--log", action="store", type=str, dest="log_level", default=DEFAULT_LOG_LEVEL, help="Log level (Default: %s)" % DEFAULT_LOG_LEVEL)

def parse_args(args=None):
    parser = argparse.ArgumentParser(description='Send results of a QuickBuild job to a LogCollector instance over TCP.')
    add_args(parser)
    return parser.parse_args(args)

def log_formatted_results(logger, results):
    tests = results.get('tests', [])
    logger.debug("NUMBER OF FORMATTED TEST RESULTS: %d" % len(tests))
    logger.debug("FAILING TESTS:\n" + pprint.pformat(list(filter(lambda x: x['result'] in QBResultsExporter.QB_FAILURE_STATUSES, tests))))

    suites = results.get('suites', [])
    logger.debug("NUMBER OF FORMATTED SUITE RESULTS: %d" % len(suites))
    logger.debug("FAILING SUITES:\n" + pprint.pformat(list(filter(lambda x: x['failures'] > 0, suites))))

def format_quickbuild_results(build_test_data, build_info):
    tests = []
    suites = {}

    for report_set in build_test_data:
        test_data = build_test_data[report_set]

        for test_details in test_data:
            status = test_details[QBResultsExporter.KEY_STATUS]
            suite = test_details[QBResultsExporter.KEY_CLASS_NAME]
            duration = test_details[QBResultsExporter.KEY_DURATION]
            package = test_details[QBResultsExporter.KEY_PACKAGE_NAME]
            product = build_info[QBResultsExporter.KEY_PRODUCT]

            test = {
                'suite': suite,
                'classname': test_details[QBResultsExporter.KEY_CLASS_NAME],
                'test': test_details[QBResultsExporter.KEY_TEST_NAME],
                'result': status,
                'message': test_details[QBResultsExporter.KEY_ERROR_MESSAGE],
                'duration': duration,
                'reportset': test_details[QBResultsExporter.KEY_REPORT_SET],
                'stage': build_info[QBResultsExporter.KEY_STAGE]
            }

            tests.append(test)

            if suite not in suites:
                suites[suite] = {
                    'failures': 0,
                    'skipped': 0,
                    'passed': 0,
                    'name': suite,
                    'test_count': 0,
                    'duration': 0,
                    'package': None,
                    'product': None
                }

            suite_result = suites[suite]

            if package and not suite_result['package']:
                suite_result['package'] = package

            if product and not suite_result['product']:
                suite_result['product'] = product

            try:
                suite_result['duration'] += int(duration)
            except:
                pass

            suite_result['test_count'] += 1

            if status in QBResultsExporter.QB_PASS_STATUSES:
                suite_result['passed'] += 1
            elif status in QBResultsExporter.QB_FAILURE_STATUSES:
                suite_result['failures'] += 1
            else:
                suite_result['skipped'] += 1

    results = {
        'tests': tests,
        'suites': list(suites.values())
    }

    return results

def quickbuild_xml_decode(build_info):
    build_id = build_info.get(QBResultsExporter.KEY_BUILD_ID, None)
    build_test_data = qb_results_exporter.get_build_test_data(build_id)
    results = format_quickbuild_results(build_test_data, build_info)
    log_formatted_results(logger, results)
    return results

def status():
    return build_info.get(QBResultsExporter.KEY_BUILD_STATUS, None)

if __name__ == '__main__':
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logger = logging.getLogger('StoreQuickBuildResults')

    try:
        args = parse_args()

        if (args.clientcert or args.clientkey) and not (args.clientcert and args.clientkey):
            raise ValueError("Either both '--clientcert' and '--clientkey' must be set or neither should be set.")

        logging.basicConfig(level=args.log_level.upper())
        qb_results_exporter = QBResultsExporter(logger, args.qb_username, args.qb_password)

        build_info = qb_results_exporter.get_build_info(args.build_id, args.product, args.stage)
        build_date = build_info.get(QBResultsExporter.KEY_BUILD_DATE_TIME_UTC, None)
        build_url = build_info.get(QBResultsExporter.KEY_BUILD_URL, None)

        if build_date:
            build_date = build_date.isoformat()

        quickbuildResults = BuildResults(platform = args.platform, jobName = args.job_name, buildId = args.build_id, buildDateTime = build_date, jobLink = build_url)
        quickbuildResults.storeTests(quickbuild_xml_decode, {'build_info': build_info})
        quickbuildResults.storeStatus(status)
        quickbuildResults.save(args.log_collect_addr, args.log_collect_port, cafile=args.cacert,
                               clientcert=args.clientcert, clientkey=args.clientkey, keypass=args.clientpassword)

    except Exception as err:
        logger.error(err)
        exit(1)

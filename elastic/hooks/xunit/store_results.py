#! /usr/bin/python3

"""
Library pushing XUnit results to logstash. Intended as a baseline for any CI systems that do not provide XUnit file ingestion that can be used instead.
"""

import sys

from junitparser import JUnitXml

from elastic.hooks.common.store_results import assemble_build, parse_args

def get_all_xunit_files(testfiles):
    """
    Takes a list of XUnit files and processes them into the BuildResults format

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
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
    return results

def get_xunit_results(filename):
    """
    Takes a single XUnit file and returns suites and tests in BuildResults format

    Args:
        testfile: the location of a single XUnit XML file
    """
    xml = JUnitXml.fromfile(filename)

    results = {
        'tests': [],
        'suites': []
    }

    for suite in xml:
<<<<<<< Updated upstream
        time = 0
        # Wrap time access in try except due to occasional string times
        try:
            time = suite.time
        except:
            pass

        suite_result = {
            'errors': suite.errors,
            'failures': suite.failures,
            'name': suite.name,
            'test_count': suite.tests,
            'duration': time

        }
        results['suites'].append(suite_result)
        for case in suite:
            time = 0
            # Wrap time access in try except due to occasional string times
            try:
                time = case.time
            except:
                pass

=======
        suite_result = {
            'failuresCount': suite.failures + suite.errors,
            'skippedCount': suite.skipped,
            'passedCount': suite.tests - (suite.failures + suite.errors),
            'totalCount': suite.tests,
            'name': suite.name,
            'duration': suite.time
        }
        results['suites'].append(suite_result)
        for case in suite:
>>>>>>> Stashed changes
            if case.result is None:
                result = "passed"
                message = ""
            else:
<<<<<<< Updated upstream
                result = case.result._tag
=======
                result = case.result.__name__
>>>>>>> Stashed changes
                message = case.result.message

            test = {
                'suite': suite.name,
                'classname': case.classname,
                'test': case.name,
                'result': result,
                'message': message,
<<<<<<< Updated upstream
                'duration': time
=======
                'duration': case.time
>>>>>>> Stashed changes
            }

            results['tests'].append(test)

    return results

def status(args):
    """
    Callback function to provide the build status to BuildResults
    """
    return args.buildstatus

def main():
    """
    Provides a CLI interface that takes in XUnit files and returns the results to logstash
    """
    args = parse_args("Send results of a Jenkins build to a LogCollector instance over TCP.")

    xunit_results = assemble_build(args, get_all_xunit_files, [args.testfiles])

    xunit_results.save_logcollect(args.logcollectaddr, args.logcollectport, cafile=args.cacert, clientcert=args.clientcert, clientkey=args.clientkey,
                                  keypass=args.clientpassword)

if __name__ == '__main__':
    sys.exit(main())

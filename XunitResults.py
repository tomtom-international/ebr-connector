#! /usr/bin/python3

from junitparser import JUnitXml

def getXunitResultsAllfiles(testfiles):
    results = {
        'tests': [],
        'suites': []
    }
    for testfile in testfiles:
        temp_results = getXunitResults(testfile)
        results['tests'].extend(temp_results['tests'])
        results['suites'].extend(temp_results['suites'])
    
    return results

def getXunitResults(filename):
    xml = JUnitXml.fromfile(filename)

    results = {
        'tests': [],
        'suites': []
    }

    for suite in xml:
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

            if case.result is None:
                result = "passed"
                message = ""
            else:
                result = case.result._tag
                message = case.result.message

            test = {
                'suite': suite.name,
                'classname': case.classname,
                'test': case.name,
                'result': result,
                'message': message,
                'duration': time
            }

            results['tests'].append(test)

    return results
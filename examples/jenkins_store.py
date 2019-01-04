import requests

from datetime import datetime

from elastic.schema.build_results import BuildResults

def status():
    return "passing"

def jenkins_json_decode(url):
    json_results = requests.get(url).json()
    results = {
        'tests': [],
        'suites': []
    }

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

            if case['status'] == "FAILED":
                failed_case_no += 1
            elif case['status'] == "SKIPPED":
                skipped_case_no += 1
            else:
                passed_case_no += 1

            results['tests'].append(test)
        suite_result = {
            'failures': failed_case_no,
            'skipped': skipped_case_no,
            'passed_case_no': passed_case_no,
            'name': suite['name'],
            'test_count': len(suite['cases']),
            'duration': suite['duration']
            }

        results['suites'].append(suite_result)

    return results

url = "https://***REMOVED***/view/baseline-jobs/job/cpp-reflection-tests-BB-baseline/lastSuccessfulBuild/testReport/api/json"

testBuild = BuildResults(jobName = "test", buildDateTime = datetime.now().isoformat(), jobLink = url)
testBuild.store_tests(jenkins_json_decode, {'url': url})
testBuild.store_status(status)

dest = 'ubuntu-logcollector.ber.global'
port = 10010

testBuild.save_logcollect(dest, port)

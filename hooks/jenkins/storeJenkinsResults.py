import requests
import argparse
from datetime import datetime
from elastic.schema.BuildResults import BuildResults
from json.decoder import JSONDecodeError


def status():
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
    parser.add_argument('--buildid', required=True, help="ID of the build")
    parser.add_argument('--jobname', required=True, help="Name of job")
    parser.add_argument('--buildtime', required=True, help="Build date-time string")
    parser.add_argument('--buildstatus', required=True, help="Build status string")
    parser.add_argument('--logcollectname', required=True, help="Address of LogCollector to send to")
    parser.add_argument('--logcollectport', required=True, help="Port on the LogCollector to send to", type=int)
    parser.add_argument('--cacert', default=None, help="Location of CA cert to verify against.")
    parser.add_argument('--clientcert', default=None, help="Client certificate file. Must also provide client key.")
    parser.add_argument('--clientkey', default=None, help="Client key file. Must also provide client certificate.")
    parser.add_argument('--clientpassword', default="", help="Client key file's password. Only use if there is a password on the keyfile.")

    args = parser.parse_args()

    if (args.clientcert or args.clientkey) and not (args.clientcert and args.clientkey):
        print("Either both '--clientcert' and '--clientkey' must be set or neither should be set.")
        exit()

    jenkinsBuild = BuildResults(jobName = args.jobname, buildId = args.buildid, buildDateTime = args.buildtime, jobLink = args.buildurl)
    jenkinsBuild.storeTests(jenkins_json_decode, {'url': args.buildurl + "testReport/api/json"})
    jenkinsBuild.storeStatus(status)

    jenkinsBuild.save(args.logcollectname, args.logcollectport, cafile=args.cacert, clientcert=args.clientcert, clientkey=args.clientkey, keypass=args.clientpassword)


if __name__ == '__main__':
    sys.exit(main())

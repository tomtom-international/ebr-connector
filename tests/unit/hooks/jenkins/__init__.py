# -*- coding: utf-8 -*-

"""Module providing some Jenkins test report in JSON format.
"""

def get_jenkins_test_report_response():
    """Returns a Jenkins test report in JSON format as it is done via the `/testreport/api/json` endpoint.
    """
    # pylint: disable=line-too-long
    return {
                "_class": "hudson.tasks.junit.TestResult",
                "testActions": [],
                "duration": 28471.805,
                "empty": False,
                "failCount": 2,
                "passCount": 33042,
                "skipCount": 279,
                "suites": [
                    {
                        "cases": [
                            {
                                "testActions": [],
                                "age": 42,
                                "className": "CMyClassTest",
                                "duration": 0.0,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 5732,
                                "name": "DISABLED_TestCase1",
                                "skipped": True,
                                "skippedMessage": "",
                                "status": "SKIPPED",
                                "stderr": None,
                                "stdout": None
                            },
                            {
                                "testActions": [],
                                "age": 0,
                                "className": "CMyClassTest",
                                "duration": 0.355,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "TestCase2",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            }
                        ],
                        "duration": 3.159,
                        "enclosingBlockNames": [],
                        "enclosingBlocks": [],
                        "id": None,
                        "name": "CMyClassTest",
                        "nodeId": None,
                        "stderr": None,
                        "stdout": None,
                        "timestamp": None
                    },
                    {
                        "cases": [
                            {
                                "testActions": [],
                                "age": 0,
                                "className": "org.acme.tests.myPackage.FeatureATest",
                                "duration": 31.053,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_scenario_1",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            },
                            {
                                "testActions": [],
                                "age": 0,
                                "className": "org.acme.tests.myPackage.FeatureATest",
                                "duration": 25.326,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_scenario_2",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            },
                            {
                                "testActions": [],
                                "age": 0,
                                "className": "org.acme.tests.myPackage.FeatureATest",
                                "duration": 73.257,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_scenario_3",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            },
                            {
                                "testActions": [],
                                "age": 0,
                                "className": "org.acme.tests.myPackage.FeatureATest",
                                "duration": 20.384,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_scenario_4",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            },
                            {
                                "testActions": [],
                                "age": 0,
                                "className": "org.acme.tests.myPackage.FeatureATest",
                                "duration": 37.284,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_scenario_5",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            }
                        ],
                        "duration": 187.346,
                        "enclosingBlockNames": ["Test worker 8", "Tests"],
                        "enclosingBlocks": ["60", "36"],
                        "id": None,
                        "name": "org.acme.tests.myPackage.FeatureATest",
                        "nodeId": "215",
                        "stderr": None,
                        "stdout": None,
                        "timestamp": "Feb 18, 2019 9:09:00 PM"
                    },
                    {
                        "cases": [
                            {
                                "testActions": [],
                                "age": 0,
                                "className": "org.acme.tests.myPackage.FeatureBTest",
                                "duration": 19.483,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_scenario_1",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            },
                            {
                                "testActions": [],
                                "age": 0,
                                "className": "org.acme.tests.myPackage.FeatureBTest",
                                "duration": 14.529,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_scenario_2",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            },
                            {
                                "testActions": [],
                                "age": 0,
                                "className": "org.acme.tests.myPackage.FeatureBTest",
                                "duration": 11.191,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_scenario_3",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            },
                            {
                                "testActions": [],
                                "age": 0,
                                "className": "org.acme.tests.myPackage.FeatureBTest",
                                "duration": 14.231,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_scenario_4",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            }
                        ],
                        "duration": 59.471,
                        "enclosingBlockNames": ["Test worker 10", "Tests"],
                        "enclosingBlocks": ["62", "36"],
                        "id": None,
                        "name": "org.acme.tests.myPackage.FeatureBTest",
                        "nodeId": "367",
                        "stderr": None,
                        "stdout": None,
                        "timestamp": "Feb 18, 2019 9:16:40 PM"
                    },
                    {
                        "cases": [
                            {
                                "testActions": [],
                                "age": 0,
                                "className": "org.acme.tests.myOtherPackage.FeatureC",
                                "duration": 8.866,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_scenario_1",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            },
                            {
                                "testActions": [],
                                "age": 0,
                                "className": "org.acme.tests.myOtherPackage.FeatureC",
                                "duration": 6.941,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_scenario_2",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            },
                            {
                                "testActions": [],
                                "age": 0,
                                "className": "org.acme.tests.myOtherPackage.FeatureC",
                                "duration": 6.321,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_scenario_3",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            },
                            {
                                "testActions": [],
                                "age": 1,
                                "className": "junit.framework.TestSuite",
                                "duration": 0.004,
                                "errorDetails": "test timed out after 10 minutes",
                                "errorStackTrace": "org.junit.runners.model.TestTimedOutException: test timed out after 10 minutes\n\tat java.lang.Object.wait(Native Method)\n\tat org.acme.test.performance.TestPerformanceManager$1.evaluate(TestPerformanceManager.java:68)\n\tat org.acme.test.testcases.CustomTestRunner.runChild(CustomTestRunner.java:145)\n\tat org.acme.test.testcases.CustomTestRunner.runChild(CustomTestRunner.java:42)\n\tat java.util.concurrent.FutureTask.run(FutureTask.java:266)\n\tat java.lang.Thread.run(Thread.java:748)\n",
                                "failedSince": 5773,
                                "name": "org.acme.tests.myOtherPackage.FeatureC",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "FAILED",
                                "stderr": None,
                                "stdout": None
                            },
                            {
                                "testActions": [],
                                "age": 1,
                                "className": "org.acme.tests.myOtherPackage.FeatureC",
                                "duration": 0.0,
                                "errorDetails": None,
                                "errorStackTrace": "org.acme.test.testrunner.TestError: Test failed due to error. RunCommandError('(pid 2685) returned 1 code.',)",
                                "failedSince": 5773,
                                "name": "testSetup",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "FAILED",
                                "stderr": None,
                                "stdout": None
                            }
                        ],
                        "duration": 22.132,
                        "enclosingBlockNames": ["Test worker 10", "Tests"],
                        "enclosingBlocks": ["62", "36"],
                        "id": None,
                        "name": "org.acme.tests.myOtherPackage.FeatureC",
                        "nodeId": "367",
                        "stderr": None,
                        "stdout": None,
                        "timestamp": "Feb 18, 2019 9:14:42 PM"
                    }
                ]
        }

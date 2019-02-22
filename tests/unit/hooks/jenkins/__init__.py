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
                                "className": "CAdminAreaNamesTest",
                                "duration": 0.0,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 5732,
                                "name": "DISABLED_Europe_incorrect",
                                "skipped": True,
                                "skippedMessage": "",
                                "status": "SKIPPED",
                                "stderr": None,
                                "stdout": None
                            },
                            {
                                "testActions": [],
                                "age": 0,
                                "className": "CAdminAreaNamesTest",
                                "duration": 0.355,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "FullAddressAt_USA",
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
                        "name": "CAdminAreaNamesTest",
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
                                "className": "***REMOVED***",
                                "duration": 31.053,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_RTE_B2R_DeviateAfterEachViaPointWithAllViaPointsOnCrossings",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            },
                            {
                                "testActions": [],
                                "age": 0,
                                "className": "***REMOVED***",
                                "duration": 25.326,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_RTE_B2R_DeviateAfterEachViaPointWithThirdViaPointOnRoad",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            },
                            {
                                "testActions": [],
                                "age": 0,
                                "className": "***REMOVED***",
                                "duration": 73.257,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_RTE_B2R_NAVKIT_14043",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            },
                            {
                                "testActions": [],
                                "age": 0,
                                "className": "***REMOVED***",
                                "duration": 20.384,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_RTE_B2R_NAVKIT_21922_a",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            },
                            {
                                "testActions": [],
                                "age": 0,
                                "className": "***REMOVED***",
                                "duration": 37.284,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_RTE_B2R_NAVKIT_21922_b",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            }
                        ],
                        "duration": 187.346,
                        "enclosingBlockNames": ["Reflection test worker 8", "Tests"],
                        "enclosingBlocks": ["60", "36"],
                        "id": None,
                        "name": "***REMOVED***",
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
                                "className": "***REMOVED***",
                                "duration": 19.483,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_EcoRouteDoesNotAbuseFerries",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            },
                            {
                                "testActions": [],
                                "age": 0,
                                "className": "***REMOVED***",
                                "duration": 14.529,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_EcoRouteMoreEfficientThanFastest",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            },
                            {
                                "testActions": [],
                                "age": 0,
                                "className": "***REMOVED***",
                                "duration": 11.191,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_EcoRouteTakesFerryWhenReasonable",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            },
                            {
                                "testActions": [],
                                "age": 0,
                                "className": "***REMOVED***",
                                "duration": 14.231,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_MoreEconomicRoadPreferredToFaster",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            }
                        ],
                        "duration": 59.471,
                        "enclosingBlockNames": ["Reflection test worker 10", "Tests"],
                        "enclosingBlocks": ["62", "36"],
                        "id": None,
                        "name": "***REMOVED***",
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
                                "className": "***REMOVED***",
                                "duration": 8.866,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_01_Updated_Incidents_Propagate",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            },
                            {
                                "testActions": [],
                                "age": 0,
                                "className": "***REMOVED***",
                                "duration": 6.941,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_11_SlipRoadSearchDirection",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "PASSED",
                                "stderr": None,
                                "stdout": None
                            },
                            {
                                "testActions": [],
                                "age": 0,
                                "className": "***REMOVED***",
                                "duration": 6.321,
                                "errorDetails": None,
                                "errorStackTrace": None,
                                "failedSince": 0,
                                "name": "test_12_SlipRoadBiDirectionalSearch",
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
                                "errorStackTrace": "***REMOVED***",
                                "failedSince": 5773,
                                "name": "***REMOVED***",
                                "skipped": False,
                                "skippedMessage": None,
                                "status": "FAILED",
                                "stderr": None,
                                "stdout": None
                            },
                            {
                                "testActions": [],
                                "age": 1,
                                "className": "***REMOVED***",
                                "duration": 0.0,
                                "errorDetails": None,
                                "errorStackTrace": "***REMOVED***",
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
                        "enclosingBlockNames": ["Reflection test worker 10", "Tests"],
                        "enclosingBlocks": ["62", "36"],
                        "id": None,
                        "name": "***REMOVED***",
                        "nodeId": "367",
                        "stderr": None,
                        "stdout": None,
                        "timestamp": "Feb 18, 2019 9:14:42 PM"
                    }
                ]
        }

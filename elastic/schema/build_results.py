# -*- coding: utf-8 -*-

"""
Serialization library to/from logstash (ElasticSearch) for build results.

The classes :class:`elastic.schema.Test`, :class:`elastic.schema.TestSuite` and :class:`elastic.schema.BuildResults`
expose factory methods that create instances of these types.

We cannot use Python constructors (`__init__`) since the underlying elasticsearch_dsl components make heavily usage
of them, for example to add meta data attributes to document instances while using the search API.

In order to still have protection against violations of the schema fields we make use of a
factory method instead to create instances of these types.
"""


import socket
import ssl
import json
import traceback
import warnings

from enum import Enum
from elasticsearch_dsl import Document, Text, InnerDoc, Float, Integer, Nested, Date, Keyword, MetaField

import elastic


class Test(InnerDoc):
    """
    Provides serialization for a single test

    Args:
        br_suite: Set (suite) the test is a part of
        br_classname: Class that the test is from
        br_test: Name of the test
        br_result: Result of the test (e.g. passed)
        br_message: Any output from the test
        br_duration: Duration in milliseconds (float) of the test
        br_reportset: (Optional) Report set the test is a part of
    """
    br_suite = Text(fields={'raw': Keyword()})
    br_classname = Text(fields={'raw': Keyword()})
    br_test = Text(fields={'raw': Keyword()})
    br_result = Text()
    br_message = Text()
    br_duration = Float()
    br_reportset = Text()


    class Result(Enum):
        """Enum for keeping the test results in sync across CI hooks.
        """

        FAILED = 1
        PASSED = 2
        SKIPPED = 3

        @staticmethod
        def create(result_str):
            """Converts a test result string into a :class:`elastic.schema.Test.Result` enum.
            """
            upper_result_str = result_str.upper()
            if upper_result_str in ["PASS", "PASSED", "SUCCESS"]:
                return Test.Result.PASSED
            if upper_result_str in ["FAILURE", "ERROR", "REGRESSION", "FAILED"]:
                return Test.Result.FAILED
            if upper_result_str in ["SKIP", "SKIPPED"]:
                return Test.Result.SKIPPED
            raise ValueError("Unknown test result value '%s'" % result_str)

    @staticmethod
    def create(suite, classname, test, result, message, duration, reportset=None):
        """
        Factory method for creating a new instance of :class:`elastic.schema.Test`.
        """

        return Test(br_suite=suite, br_classname=classname, br_test=test, br_result=result, br_message=message,
                    br_duration=duration, br_reportset=reportset)


class TestSuite(InnerDoc):
    """
    Provides serialization for Test Sets (test suites)

    Args:
        br_name: Name of the suite
        br_failures_count: Number of failing tests
        br_skipped_count: Number of skipped tests
        br_passed_count: Number of passed tests
        br_total_count: Total number of tests
        br_duration: Duration in milliseconds (float) of the entire test suite
        br_package: (Optional) package the test set is associated with
    """
    br_name = Text(fields={'raw': Keyword()})
    br_failures_count = Integer()
    br_skipped_count = Integer()
    br_passed_count = Integer()
    br_total_count = Integer()
    br_duration = Float()
    br_package = Text(fields={'raw': Keyword()})

    @staticmethod
    def create(name, failures_count, skipped_count, passed_count, total_count, duration, package=None):
        """
        Factory method for creating a new instance of :class:`elastic.schema.TestSuite`.
        """
        return TestSuite(br_name=name, br_failures_count=failures_count, br_skipped_count=skipped_count,
                         br_passed_count=passed_count, br_total_count=total_count, br_duration=duration, br_package=package)



class BuildResults(Document):
    """
    Top level serialization for build results

    Args:
        br_job_name: Name of the job that owns the build being recorded (eg. Jenkins job name or QuickBuild configuration name)
        br_job_link: Link to the job on the CI system that executed it
        br_job_info: Additional information about the job. (eg. 'B.1234.COMMIT-1234')
        br_source: The source which caused the job to be triggered (eg. PR id or branch name)
        br_build_date_time: Execution time of the build (ISO-8601 format recommended)
        br_build_id: ID of the build
        br_platform: Platform of the build
        br_product: Product the build is associated with
        br_status: Status of the build (eg. if one test failed the overall build status should as well be failed)
        br_suites: Set of test suites
        br_tests_passed: Set of passed test cases
        br_tests_failed: Set of failed test cases
        br_tests_skipped: Set of skipped test cases
        br_version: Version of the BuildResults schema.
    """
    br_job_name = Text(fields={'raw': Keyword()})
    br_job_link = Keyword()
    br_job_info = Text(fields={'raw': Keyword()})
    br_source = Text(fields={'raw': Keyword()})
    br_build_date_time = Date()
    br_build_id = Keyword()
    br_platform = Text(fields={'raw': Keyword()})
    br_product = Text(fields={'raw': Keyword()})
    br_status = Keyword()
    br_suites = Nested(TestSuite)
    br_tests_passed = Nested(Test)
    br_tests_failed = Nested(Test)
    br_tests_skipped = Nested(Test)
    br_version = Keyword()


    # pylint: disable=too-few-public-methods
    class Meta:
        """Stores the plain template version in the generated index template. We cannot use the builtin `version` field
        since it is of type `integer` and we use semantic versioning.
        This data is for pure information purposes and won't be used at all by Elasticsearch.
        See as well https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-meta-field.html#mapping-meta-field.
        """
        meta = MetaField(template_version=elastic.__version__)


    class BuildStatus(Enum):
        """
        Status of a build
        """
        ABORTED = 1
        FAILURE = 2
        NOT_BUILT = 3
        RUNNING = 4
        SUCCESS = 5
        TIMEOUT = 6
        UNSTABLE = 7


        @staticmethod
        def create(build_status_str):
            """
            Converts a build status string into a :class:`elastic.schema.BuildResults.BuildStatus` enum.
            """
            upper_build_status_str = build_status_str.upper()
            if upper_build_status_str in ["SUCCESS"]:
                status = BuildResults.BuildStatus.SUCCESS
            elif upper_build_status_str in ["FAILURE", "FAILED"]:
                status = BuildResults.BuildStatus.FAILURE
            elif upper_build_status_str in ["ABORT", "ABORTED", "CANCEL", "CANCELLED"]:
                status = BuildResults.BuildStatus.ABORTED
            elif upper_build_status_str in ["NOT_BUILT", "SKIPPED"]:
                status = BuildResults.BuildStatus.NOT_BUILT
            elif upper_build_status_str in ["UNSTABLE"]:
                status = BuildResults.BuildStatus.UNSTABLE
            elif upper_build_status_str in ["TIMEOUT", "TIMEDOUT"]:
                status = BuildResults.BuildStatus.TIMEOUT
            elif upper_build_status_str in ["RUNNING", "BUILDING"]:
                status = BuildResults.BuildStatus.RUNNING
            else:
                raise ValueError("Unknown build status string '%s'" % build_status_str)
            return status


    @staticmethod
    def create(job_name, job_link, build_date_time, build_id, platform, product=None):
        """
        Creates an immutable instance of :class:`elastic.schema.BuildResults`.
        """
        return BuildResults(br_job_name=job_name, br_job_link=job_link, br_build_date_time=build_date_time, br_build_id=build_id,
                            br_platform=platform, br_product=product, br_status=None, br_suites=[], br_tests_passed=[], br_tests_failed=[], br_tests_skipped=[],
                            br_version=elastic.__version__)

    def store_tests(self, retrieve_function, *args, **kwargs):
        """
        Retrieves the test results of a build and adds them to the :class:`elastic.schema.BuildResults` object

        Args:
            retrieve_function: Callback function which provides test and suite data in dictionaries
            (see Test and TestSuite documentation for format)
        """
        try:
            results = retrieve_function(*args, **kwargs)
            for test in results.get('tests', None):
                if Test.Result[test['result']] == Test.Result.PASSED:
                    self.br_tests_passed.append(Test.create(**test))
                elif Test.Result[test['result']] == Test.Result.FAILED:
                    self.br_tests_failed.append(Test.create(**test))
                else:
                    self.br_tests_skipped.append(Test.create(**test))
            for suite in results.get('suites', None):
                self.br_suites.append(TestSuite.create(**suite))

        except  (KeyError, TypeError):
            warnings.warn("Failed to retrieve test data.")
            traceback.print_exc()

    def store_status(self, status_function, *args, **kwargs):
        """
        Retrieves the status of a build and adds it to the :class:`elastic.schema.BuildResults` object

        Args:
            status_function: Callback function which provides status information
        """
        try:
            self.br_status = status_function(*args, **kwargs)
        except (KeyError, TypeError):
            warnings.warn("Failed to retrieve status information.")
            traceback.print_exc()

    def save_logcollect(self, dest, port, cafile=None, clientcert=None, clientkey=None, keypass="", timeout=10):
        """
        Saves the :class:`elastic.schema.BuildResults` object to a LogCollector instance.

        Args:
            dest: URL/IP of the LogCollector server
            port: port of the raw intake on the LogCollector server
            cafile: (optional) file location of the root CA certificate that signed the
            LogCollector's certificate (or the LogCollector's certificate if self-signed)
            clientcert: (optional) file location of the client certificate
            clientkey: (optional) file location of the client key
            keypass: (optional) password of the client key (leave blank if unset)
            timeout: (optional) socket timeout in seconds for the write operation (10 seconds if unset)
        """

        result = str.encode(json.dumps(self.to_dict()))
        bare_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bare_socket.settimeout(timeout)

        context = ssl.create_default_context(cafile=cafile)

        if clientcert:
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_cert_chain(clientcert, clientkey, keypass)

        secure_socket = context.wrap_socket(bare_socket, server_hostname=dest)

        secure_socket.connect((dest, port))
        secure_socket.send(result)
        secure_socket.close()

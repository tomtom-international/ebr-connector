# -*- coding: utf-8 -*-

"""
Serialization library to/from logstash (ElasticSearch) for build results
"""


import socket
import ssl
import json
import traceback
import warnings

from elasticsearch_dsl import Document, Text, InnerDoc, Float, Integer, Nested, Date, Keyword

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
        br_stage: (Optional) Stage during which the test was executed
    """
    br_suite = Text(fields={'raw': Keyword()})
    br_classname = Text(fields={'raw': Keyword()})
    br_test = Text(fields={'raw': Keyword()})
    br_result = Text()
    br_message = Text()
    br_duration = Float()
    br_reportset = Text()
    br_stage = Text(fields={'raw': Keyword()})

    @staticmethod
    def create(suite, classname, test, result, message, duration, reportset=None, stage=None):
        """
        Factory method for creating a new instance of :class:`elastic.schema.Test`.

        Args:
            suite: Set (suite) the test is a part of
            classname: Class that the test is from
            test: Name of the test
            result: Result of the test (e.g. passed)
            message: Any output from the test
            duration: Duration in milliseconds (float) of the test
            reportset: (Optional) Report set the test is a part of
            stage: (Optional) Stage during which the test was executed
        """

        return Test(br_suite=suite, br_classname=classname, br_test=test, br_result=result, br_message=message,
                    br_duration=duration, br_reportset=reportset, br_stage=stage)


class TestSuite(InnerDoc):
    """
    Provides serialization for Test Sets (test suites)

    Args:
        br_name: Name of the suite
        br_failuresCount: Number of failing tests
        br_skippedCount: Number of skipped tests
        br_passedCount: Number of passed tests
        br_totalCount: Total number of tests
        br_duration: Duration in milliseconds (float) of the entire test suite
        br_package: (Optional) package the test set is associated with
        br_product: (Optional) product the test set is associated with
    """
    br_name = Text(fields={'raw': Keyword()})
    br_failuresCount = Integer()
    br_skippedCount = Integer()
    br_passedCount = Integer()
    br_totalCount = Integer()
    br_duration = Float()
    br_package = Text(fields={'raw': Keyword()})
    br_product = Text(fields={'raw': Keyword()})

    @staticmethod
    # pylint: disable=invalid-name
    def create(name, failuresCount, skippedCount, passedCount, totalCount, duration, package=None, product=None):
        """
        Factory method for creating a new instance of :class:`elastic.schema.TestSuite`.

        Args:
            name: Name of the suite
            failuresCount: Number of failing tests
            skippedCount: Number of skipped tests
            passedCount: Number of passed tests
            totalCount: Total number of tests
            duration: Duration in milliseconds (float) of the entire test suite
            package: (Optional) package the test set is associated with
            product: (Optional) product the test set is associated with
        """
        return TestSuite(br_name=name, br_failuresCount=failuresCount, sbr_kippedCount=skippedCount,
                         br_passedCount=passedCount, br_totalCount=totalCount, br_duration=duration, br_package=package,
                         br_product=product)



class BuildResults(Document):
    """
    Top level serialization for build results
    """
    br_jobName = Text(fields={'raw': Keyword()})
    br_jobLink = Keyword()
    br_buildDateTime = Date()
    br_buildId = Keyword()
    br_platform = Text(fields={'raw': Keyword()})
    br_status = Keyword()
    br_tests = Nested(Test)
    br_suites = Nested(TestSuite)
    br_version = Keyword()


    @staticmethod
    # pylint: disable=invalid-name
    def create(jobName, jobLink, buildDateTime, buildId, platform=None):
        """Creates an immutable instance of :class:`elastic.schema.BuildResults`.

        Args:
            jobName: Name of the job that owns the build being recorded
            jobLink: Link to the job on the CI system that executed it
            buildDateTime: Execution time of the build (ISO-8601 format recommended)
            buildId: Unique ID of the build
            platform: (Optional) Platform of the build
        """
        return BuildResults(br_jobName=jobName, br_jobLink=jobLink, br_buildDateTime=buildDateTime, br_buildId=buildId,
                            br_platform=platform, br_status=None, br_tests=[], br_suites=[], br_version=elastic.__version__)

    def store_tests(self, retrieve_function, *args, **kwargs):
        """
        Retrieves the test results of a build and adds them to the BuildResults object

        Args:
            retrieve_function: Callback function which provides test and suite data in dictionaries
            (see Test and TestSuite documentation for format)
        """
        try:
            results = retrieve_function(*args, **kwargs)
            for test in results.get('tests', None):
                self.br_tests.append(Test.create(**test))
            for suite in results.get('suites', None):
                self.br_suites.append(TestSuite.create(**suite))
        except  (KeyError, TypeError):
            warnings.warn("Failed to retrieve test data.")
            traceback.print_exc()

    def store_status(self, status_function, *args, **kwargs):
        """
        Retrieves the status of a build and adds it to the BuildResults object

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
        Saves the BuildResults object to a LogCollector instance.

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

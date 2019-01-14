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
    """
    br_suite = Text(fields={'raw': Keyword()})
    br_classname = Text(fields={'raw': Keyword()})
    br_test = Text(fields={'raw': Keyword()})
    br_result = Text()
    br_message = Text()
    br_duration = Float()
    br_reportset = Text()

    @staticmethod
    def create(suite, classname, test, result, message, duration, reportset=None):
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
        br_product: (Optional) product the test set is associated with
    """
    br_name = Text(fields={'raw': Keyword()})
    br_failures_count = Integer()
    br_skipped_count = Integer()
    br_passed_count = Integer()
    br_total_count = Integer()
    br_duration = Float()
    br_package = Text(fields={'raw': Keyword()})

    @staticmethod
    def create(name, failures_count, skipped_count, passed_count, total_count, duration, package=None, product=None):
        """
        Factory method for creating a new instance of :class:`elastic.schema.TestSuite`.

        Args:
            name: Name of the suite
            failures_count: Number of failing tests
            skipped_count: Number of skipped tests
            passed_count: Number of passed tests
            total_count: Total number of tests
            duration: Duration in milliseconds (float) of the entire test suite
            package: (Optional) package the test set is associated with
        """
        return TestSuite(br_name=name, br_failures_count=failures_count, br_skipped_count=skipped_count,
                         br_passed_count=passed_count, br_total_count=total_count, br_duration=duration, br_package=package,
                         br_product=product)



class BuildResults(Document):
    """
    Top level serialization for build results
    """
    br_job_name = Text(fields={'raw': Keyword()})
    br_job_link = Keyword()
    br_job_info = Text(fields={'raw': Keyword()})
    br_source = Text(fields={'raw': Keyword()})
    br_build_date_time = Date()
    br_build_id = Keyword()
    br_platform = Text(fields={'raw': Keyword()})
    br_status = Keyword()
    br_tests = Nested(Test)
    br_suites = Nested(TestSuite)
    br_version = Keyword()
    br_product = Text(fields={'raw': Keyword()})


    @staticmethod
    def create(job_name, job_link, build_date_time, build_id, platform):
        """Creates an immutable instance of :class:`elastic.schema.BuildResults`.

        Args:
            job_name: Name of the job that owns the build being recorded (eg. Jenkins job name or QuickBuild configuration name)
            job_link: Link to the job on the CI system that executed it
            job_info: Additional information about the job. (eg. 'B.1234.COMMIT-1234')
            source: The source which caused the job to be triggered (eg. PR id, branch name)
            build_date_time: Execution time of the build (ISO-8601 format recommended)
            build_id: ID of the build
            platform: Platform of the build
        """
        return BuildResults(br_job_name=job_name, br_job_link=job_link, br_build_date_time=build_date_time, br_build_id=build_id,
                            br_platform=platform, br_status=None, br_tests=[], br_suites=[], br_version=elastic.__version__, br_product=None)

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

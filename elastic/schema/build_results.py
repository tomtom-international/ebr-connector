"""
Serialization library to/from logstash (ElasticSearch) for build results
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import ssl
import json
import traceback
import warnings

from elasticsearch_dsl import Document, Text, InnerDoc, Float, Integer, Nested, Date, Keyword


class _InnerDocFrozen(InnerDoc):
    """
    Update the InnerDoc class to be frozen
    """

    def __setattr__(self, key, value):
        """
        Overridden to prevent accidential schema modifications
        """
        if not hasattr(self, key):
            raise TypeError("%r is a frozen class" % self)
        object.__setattr__(self, key, value)


class Test(_InnerDocFrozen):
    """
    Provides serialization for a single test

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
    suite = Text(fields={'raw': Keyword()})
    classname = Text(fields={'raw': Keyword()})
    test = Text(fields={'raw': Keyword()})
    result = Text()
    message = Text()
    duration = Float()
    reportset = Text()
    stage = Text(fields={'raw': Keyword()})

    def __init__(
            self,
            suite,
            classname,
            test,
            result,
            message,
            duration,
            reportset=None,
            stage=None):
        _InnerDocFrozen.__init__(
            self,
            suite=suite,
            classname=classname,
            test=test,
            result=result,
            message=message,
            duration=duration,
            reportset=reportset,
            stage=stage)


class TestSuite(_InnerDocFrozen):
    """
    Provides serialization for Test Sets (test suites)

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
    name = Text(fields={'raw': Keyword()})
    failuresCount = Integer()
    skippedCount = Integer()
    passedCount = Integer()
    totalCount = Integer()
    duration = Float()
    package = Text(fields={'raw': Keyword()})
    product = Text(fields={'raw': Keyword()})

    def __init__(
            self,
            name,
            failures,
            skipped,
            passed,
            total,
            duration,
            package=None,
            product=None):
        _InnerDocFrozen.__init__(
            self,
            name=name,
            failures=failures,
            skipped=skipped,
            passed=passed,
            total=total,
            duration=duration,
            package=package,
            product=product)


class BuildResults(Document):
    """
    Top level serialization for build results

    Args:
        jobName: Name of the job that owns the build being recorded
        jobLink: Link to the job on the CI system that executed it
        buildDateTime: Execution time of the build (ISO-8601 format recommended)
        buildId: Unique ID of the build
        platform: (Optional) Platform of the build
    """
    jobName = Text(fields={'raw': Keyword()})
    jobLink = Text()
    buildDateTime = Date()
    buildId = Text(fields={'raw': Keyword()})
    platform = Text(fields={'raw': Keyword()})
    status = Keyword()
    tests = Nested(Test)
    suites = Nested(TestSuite)

    def __init__(
            self,
            jobName,
            jobLink,
            buildDateTime,
            buildId,
            platform=None):
        Document.__init__(
            self,
            jobName=jobName,
            jobLink=jobLink,
            buildDateTime=buildDateTime,
            buildId=buildId,
            platform=platform)

    def __setattr__(self, key, value):
        if not hasattr(self, key):
            raise TypeError("%r is a frozen class" % self)
        object.__setattr__(self, key, value)

    def store_tests(self, retrieve_function, *args, **kwargs):
        """
        Retrieves the test results of a build and adds them to the BuildResults object

        Args:
            retrieveFunction: Callback function which provides test and suite data in dictionaries
            (see Test and TestSuite documentation for format)
        """
        try:
            results = retrieve_function(*args, **kwargs)
            for test in results.get('tests', None):
                self.tests.append(Test(**test))
            for suite in results.get('suites', None):
                self.suites.append(TestSuite(**suite))
        except Exception:
            warnings.warn("Failed to retrieve test data.")
            traceback.print_exc()

    def store_status(self, status_function, *args, **kwargs):
        """
        Retrieves the status of a build and adds it to the BuildResults object

        Args:
            statusFunction: Callback function which provides status information
        """
        try:
            self.status = status_function(*args, **kwargs)
        except Exception:
            warnings.warn("Failed to retrieve status information.")
            traceback.print_exc()

    def save_logcollect(
            self,
            dest,
            port,
            cafile=None,
            clientcert=None,
            clientkey=None,
            keypass=""):
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
        """
        result = str.encode(json.dumps(self.to_dict()))
        bare_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bare_socket.settimeout(10)

        context = ssl.create_default_context(cafile=cafile)

        if clientcert:
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_cert_chain(clientcert, clientkey, keypass)

        secure_socket = context.wrap_socket(bare_socket, server_hostname=dest)

        secure_socket.connect((dest, port))
        secure_socket.send(result)
        secure_socket.close()

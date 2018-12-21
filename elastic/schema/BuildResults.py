#!/usr/bin/env python
# -*- coding: utf-8 -*-

from elasticsearch_dsl import Document, Text, InnerDoc, Float, Integer, Nested, Date, Keyword

import socket
import ssl
import json
import traceback
import warnings

class InnerDocFrozen(InnerDoc):
    """
    Update the InnerDoc class to be frozen
    """
    def __setattr__(self, key, value):
        if not hasattr(self, key):
            raise TypeError( "%r is a frozen class" % self )
        object.__setattr__(self, key, value)

class Test(InnerDocFrozen):
    suite = Text(fields={'raw': Keyword()})
    classname = Text(fields={'raw': Keyword()})
    test = Text(fields={'raw': Keyword()})
    result = Text()
    message = Text()
    duration = Float()
    reportset = Text()
    stage = Text(fields={'raw': Keyword()})

    def __init__(self, suite, classname, test, result, message, duration, reportset = None, stage = None):
        """
        Construct Test class

        Args:
            suite: Set the test is a part of
            classname: Class that the test is from
            test: Name of the test
            result: Result of the test (e.g. passed)
            message: Any output from the test
            duration: Duration in miliseconds (float) of the test
            reportset: (Optional) Report set the test is a part of
            stage: (Optional) Stage during which the test was executed
        """
        InnerDocFrozen.__init__(self, suite = suite, classname = classname, test = test, result = result, message = message, duration = duration, \
        reportset = reportset, stage = stage)

class TestSuite(InnerDocFrozen):
    name = Text(fields={'raw': Keyword()})
    failures = Integer()
    skipped = Integer()
    passed = Integer()
    total = Integer()
    duration = Float()
    package = Text(fields={'raw': Keyword()})
    product = Text(fields={'raw': Keyword()})

    def __init__(self, name, failures, skipped, passed, total, duration, package = None, product = None):
        """
        Constructs TestSuite class

        Args:
            name: Name of the suite
            failures: Number of failing tests
            skipped: Number of skipped tests
            passed: Number of passed tests
            total: Total number of tests
            duration: Duration in miliseconds (float) of the entire test suite
            package: (Optional) package the test set is associated with
            product: (Optional) product the test set is associated with
        """
        InnerDocFrozen.__init__(self, name = name, failures = failures, skipped = skipped, passed = passed, total = total, duration = duration, \
        package = package, product = product)

class BuildResults(Document):
    jobName = Text(fields={'raw': Keyword()})
    jobLink = Text()
    buildDateTime = Date()
    buildId = Text(fields={'raw': Keyword()})
    platform = Text(fields={'raw': Keyword()})
    status = Keyword()
    tests = Nested(Test)
    suites = Nested(TestSuite)

    def __init__(self, jobName, jobLink, buildDateTime, buildId, platform = None):
        """
        Constructs BuildResults class

        Args:
            jobName: Name of the job that owns the build being recorded
            jobLink: Link to the job on the CI system that executed it
            buildDateTime: Execution time of the build
            buildId: Unique ID of the build
            platform: (Optional) Platform of the build

        """
        Document.__init__(self, jobName = jobName, jobLink = jobLink, buildDateTime = buildDateTime, buildId = buildId, platform = platform)

    def __setattr__(self, key, value):
        if not hasattr(self, key):
            raise TypeError( "%r is a frozen class" % self )
        object.__setattr__(self, key, value)

    def storeTests(self, retrieveFunction, args):
        """
        Retrieves the test results of a build and adds them to the BuildResults object

        Args:
            retrieveFunction: Callback function which provides test and suite data in dictionaries (see Test and TestSuite documentation for format)
        """
        try:
            results = retrieveFunction(**args)
            for test in results.get('tests', None):
                self.tests.append(Test(**test))
            for suite in results.get('suites', None):
                self.suites.append(TestSuite(**suite))
        except Exception as e:
            warnings.warn("Failed to retrieve test data.")
            traceback.print_exc()

    def storeStatus(self, statusFunction):
        """
        Retrieves the status of a build and adds it to the BuildResults object

        Args:
            statusFunction: Callback function which provides status information
        """
        try:
            self.status = statusFunction()
        except:
        except Exception as e:
            warnings.warn("Failed to retrieve status information.")
            traceback.print_exc()

    def save(self, dest, port, cafile=None, clientcert=None, clientkey=None, keypass=""):
        """
        Saves the BuildResults object to a LogCollector instance.

        Args:
            dest: URL/IP of the LogCollector server
            port: port of the raw intake on the LogCollector server
            cafile: (optional) file location of the root CA cert that signed the LogCollector's cert (or the LogCollector's cert if self-signed)
            clientcert: (optional) file location of the client certificate
            clientkey: (optional) file location of the client key
            keypass: (optional) password of the client key (leave blank if unset)
        """
        result=str.encode(json.dumps(self.to_dict()))
        bareSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bareSocket.settimeout(10)

        context = ssl.create_default_context(cafile=cafile)

        if clientcert:
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_cert_chain(clientcert, clientkey, keypass)

        secureSocket = context.wrap_socket(bareSocket, server_hostname=dest)

        secureSocket.connect((dest, port))
        secureSocket.send(result)
        secureSocket.close()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from elasticsearch_dsl import Document, Text, InnerDoc, Float, Integer, Nested, Date, Keyword

import socket
import ssl
import json
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

class TestSuite(InnerDocFrozen):
    name = Text(fields={'raw': Keyword()})
    failures = Integer()
    skipped = Integer()
    passed = Integer()
    total = Integer()
    duration = Float()
    package = Text(fields={'raw': Keyword()})
    product = Text(fields={'raw': Keyword()})

class BuildResults(Document):
    jobName = Text(fields={'raw': Keyword()})
    jobLink = Text()
    buildDateTime = Date()
    buildId = Text(fields={'raw': Keyword()})
    platform = Text(fields={'raw': Keyword()})
    status = Keyword()
    tests = Nested(Test)
    suites = Nested(TestSuite)

    def __setattr__(self, key, value):
        if not hasattr(self, key):
            raise TypeError( "%r is a frozen class" % self )
        object.__setattr__(self, key, value)

    def storeTests(self, retrieveFunction, args):
        try:
            results = retrieveFunction(**args)
            for test in results.get('tests', None):
                self.tests.append(Test(**test))
            for suite in results.get('suites', None):
                self.suites.append(TestSuite(**suite))
        except Exception as e:
            warnings.warn("Failed to retrieve test data.")
            warnings.warn(e)

    def storeStatus(self, statusFunction):
        try:
            self.status = statusFunction()
        except:
            warnings.warn("Failed to retrieve status information.")

    def save(self, dest, port, cafile=None, clientcert=None, clientkey=None, keypass=""):
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

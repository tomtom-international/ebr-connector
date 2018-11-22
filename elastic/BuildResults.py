from elasticsearch_dsl import Document, Text, InnerDoc, Float, Integer, Nested, Date

import socket
import json
import warnings

class Test(InnerDoc):
    suite = Text()
    classname = Text()
    test = Text()
    result = Text()
    message = Text()
    duration = Float()

class TestSuite(InnerDoc):
    errors = Text()
    failures = Text()
    name = Text()
    test_count = Integer()
    duration = Float()

class BuildResults(Document):
    jobName = Text()
    jobLink = Text()
    buildDateTime = Date()
    buildId = Text()
    status = Text()
    tests = Nested(Test)
    suites = Nested(TestSuite)

    def storeTests(self, retrieveFunction, args):
        try:
            results = retrieveFunction(**args)
            for test in results.get('tests', None):
                self.tests.append(Test(**test))
            for suite in results.get('suites', None):
                self.suites.append(TestSuite(**suite))
        except:
            warnings.warn("Failed to retrieve test data.")

    def storeStatus(self, statusFunction):
        try:
            self.status = statusFunction()
        except:
            warnings.warn("Failed to retrieve status information.")

    def save(self, dest, port):
        result=str.encode(json.dumps(self.to_dict()))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((dest, port))
        s.send(result)
        s.close()

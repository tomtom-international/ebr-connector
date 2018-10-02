from elasticsearch_dsl import Document, Text, InnerDoc, Float, Integer, Nested, Date

import socket
import json

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
    status = Text()
    tests = Nested(Test)
    suites = Nested(TestSuite)

    class Index:
        name = 'test_buildresults'
    
    def storeTests(self, retrieveFunction, args):
        results = retrieveFunction(**args)
        for test in results.get('tests', None):
            self.tests.append(Test(**test))
        for suite in results.get('suites', None):
            self.suites.append(TestSuite(**suite))

    def storeStatus(self, statusFunction):
        self.status = statusFunction()

    def save(self, dest, port):
        result=str.encode(json.dumps(self.to_dict()))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((dest, port))
        s.send(result)
        s.close()
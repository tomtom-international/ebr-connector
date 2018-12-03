from elasticsearch_dsl import Document, Text, InnerDoc, Float, Integer, Nested, Date

import socket
import ssl
import json
import warnings

class Test(InnerDoc):
    suite = Text()
    classname = Text()
    test = Text()
    result = Text()
    message = Text()
    duration = Float()
    reportset = Text()
    stage = Text()

class TestSuite(InnerDoc):
    failures = Integer()
    passed = Integer()
    skipped = Integer()
    name = Text()
    test_count = Integer()
    duration = Float()
    package = Text()
    product = Text()

class BuildResults(Document):
    platform = Text()
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

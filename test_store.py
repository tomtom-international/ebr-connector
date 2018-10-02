from datetime import datetime

from elasticsearch_dsl import connections

from XunitResults import getXunitResultsAllfiles
from BuildResults import BuildResults

#connections.create_connection(hosts=['https://jenkins:test@localhost:9200'], verify_certs=False, timeout=20)

def status():
    return "passing"

testBuild = BuildResults(jobName = "test", buildDateTime = datetime.now().isoformat(), jobLink = "https://***REMOVED***/")
testBuild.storeTests(getXunitResultsAllfiles, {'testfiles': ["test/passed.xml"]})
testBuild.storeStatus(status)

dest = 'ubuntu-logcollector.ber.global'
port = 10010

testBuild.save(dest, port)
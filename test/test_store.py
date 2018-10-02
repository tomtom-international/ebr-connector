from elasticsearch_dsl import connections

from XunitResults import getXunitResults
from BuildResults import BuildResults

connections.create_connection(hosts=['https://jenkins:test@localhost:9200'], verify_certs=False, timeout=20)

testBuild = BuildResults(jobName = "test")
testBuild.storeTests(["test/passed.xml"])
testBuild.save()
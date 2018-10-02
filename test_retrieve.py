from elasticsearch_dsl import connections

from BuildResults import BuildResults

connections.create_connection(hosts=['https://jenkins:test@localhost:9200'], verify_certs=False, timeout=20)

search = BuildResults.search()
search = search.query('match', jobName="test")

results = search.execute()

for job in results:
    print(job.jobName, job.buildDateTime, job.status)
    #for test in job.tests:
    #    print(test.result)
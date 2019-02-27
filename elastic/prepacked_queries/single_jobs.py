"""
Collection of queries that return a single result (in dictionary form)
"""

from elasticsearch_dsl import Q

from elastic.prepacked_queries.query import make_query, DETAILED_JOB

def get_job(index, job_key):
    """
    Get result of a single job from the elastic search database by its key
    Args:
        index: Elastic search index to use
        job: key of for the job to get results of
    Returns:
        A single dict of the results from the job requested
    """
    match_jobkey = Q("match", br_job_url_key=job_key)
    job_result = make_query(index, match_jobkey, DETAILED_JOB['includes'], DETAILED_JOB['excludes'])

    return job_result[0]

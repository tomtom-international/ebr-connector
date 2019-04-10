"""
Collection of queries that return a single result (in dictionary form)
"""

import warnings
from elasticsearch_dsl import Q

from ebr_connector.prepacked_queries.query import make_query, DETAILED_JOB

warnings.warn("prepacked_queries: the single_jobs module is deprecated", DeprecationWarning, stacklevel=2)

def get_build(index, job_name, build_id, wildcard=False):
    """
    Get result of a single build from the elastic search database by its ID and the name of the job it belongs to.

    Args:
        index: Elastic search index to use
        job_name: Name of job to search within
        build_id: ID of the build
        wildcard: When true, search with wildcard instead of exact match
    Returns:
        A single dict of the results from the build requested
    """
    search_type = "term"
    if wildcard:
        search_type = "wildcard"
    match_job_name = Q(search_type, br_job_name__raw=job_name)
    match_build_id = Q(search_type, br_build_id_key=build_id)
    combined_filter = match_job_name + match_build_id
    result = make_query(index, combined_filter, includes=DETAILED_JOB['includes'], excludes=DETAILED_JOB['excludes'], size=1)

    return result[0]

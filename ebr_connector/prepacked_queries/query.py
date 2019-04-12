"""
Module with basic wrapper for making a query to elastic search, as well as default field lists for including/excluding in results
"""

from deprecated.sphinx import deprecated
from ebr_connector.schema.build_results import BuildResults
from ebr_connector.prepacked_queries import DEPRECATION_MESSAGE


# Provides common job details, without all passing and skipped tests
DETAILED_JOB = {
    "includes": [
        "br_build_date_time",
        "br_job_name",
        "br_job_url_key",
        "br_source",
        "br_build_id_key",
        "br_platform",
        "br_product",
        "br_status_key",
        "br_version_key",
        "br_tests_object"
    ],
    "excludes": [
        "lhi*",
        "br_tests_object.br_tests_passed_object.*",
        "br_tests_object.br_tests_skipped_object.*",
        "br_tests_object.br_suites_object.*"
    ]
}

JOB_MINIMAL = {
    "includes": [
        "br_job_name",
        "br_build_id_key",
        "br_status_key",
        "br_build_date_time"
    ],
    "excludes": [
    ]
}


@deprecated(version="0.1.1", reason=DEPRECATION_MESSAGE)
def make_query(index, combined_filter, includes, excludes, agg=None, size=1):
    """
    Simplifies the execution and usage of a typical query, including cleaning up the results.

    Args:
        index: index to search on
        combined_filter: combined set of filters to run the query with
        includes: list of fields to include on the results (keep as  small as possible to improve execution time)
        excludes: list of fields to explicitly exclude from the results
        size: [Optional] number of results to return. Defaults to 1.
    Returns:
        List of dicts with results of the query.
    """
    search = BuildResults().search(index=index)
    search = search.source(includes=includes, excludes=excludes)
    if agg:
        search = search.aggs.metric('fail_count', agg)
    search = search.query("bool", filter=[combined_filter])[0:1] # pylint: disable=no-member
    search = search[0:size]
    response = search.execute()
    results = []

    if agg:
        results = response['aggregations']['fail_count']['buckets']
    else:
        for hit in response['hits']['hits']:
            results.append(hit['_source'])
    return results

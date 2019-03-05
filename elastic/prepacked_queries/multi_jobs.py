"""
A collection of queries that provide multiple results as an array of dicts
"""
from elasticsearch_dsl import Q, A

from elastic.schema.build_results import BuildResults
from elastic.prepacked_queries.query import make_query, DETAILED_JOB

def successful_jobs(index, job_name_regex, size=10, start_date="now-7d", end_date="now"):
    """
    Get the results of jobs matching the job name regex provided.
    Args:
        index: Elastic search index to use
        job_name_regex: Regex for elastic search to match against
        size: [Optional] Number of results to return. Default is 10.
        start_date: [Optional] Specify start date (string in elastic search format). Default is 7 days ago.
        end_data: [Optional] Specify end date (string in elastic search format). Default is now.
    Returns:
        An array of dicts of the matching jobs
    """
    ## Search for all jobs that fullfil the regex. The regex is evaluated on the keyword field (`raw`) of the field `br_job_name`.
    match_jobname = Q("regexp", br_job_name__raw=job_name_regex)
    ## and have the following build status
    match_status = Q("match", br_status_key=BuildResults.BuildStatus.SUCCESS.name)

    range_time = Q("range", **{"br_build_date_time": {"gte": start_date, "lt": end_date}})

    combined_filter = match_jobname & match_status & range_time

    result = make_query(index, combined_filter, includes=DETAILED_JOB['includes'], excludes=DETAILED_JOB['excludes'], size=size)
    return result

def failed_tests(index, job_name, size=10, fail_count=5, duration_low=162.38, duration_high=320, start_date="now-7d", end_date="now", agg=False): #pylint: disable=too-many-locals
    """
    Get jobs with failed tests matching certain parameters
    Args:
        index: Elastic search index to use
        job_name: Job name to evaluate
        size: [Optional] Number of results to return. Default is 10.
        fail_count: [Optional] Minimum number of failures for inclusion. Default is 5.
        duration_low: [Optional] Minimum test duration for inclusion in results. Default is 162.38
        duration_high: [Optional] Maximum test duration for inclusion in results. Default is 320.
        start_date: [Optional] Specify start date (string in elastic search format). Default is 7 days ago.
        end_data: [Optional] Specify end date (string in elastic search format). Default is now.
        agg: [Optional] Converts the query to an aggregation query over the tests.
    Returns:
        An array of dicts of the matching jobs
    """
     ## Search for the exact job name
    match_jobname = Q("term",
                      br_job_name__raw=job_name)
    ## Search for "failure", "FAILURE", "unstable", "UNSTABLE"
    match_status = Q("match", br_status_key=BuildResults.BuildStatus.FAILURE.name) | Q("match", br_status_key=BuildResults.BuildStatus.UNSTABLE.name)
    ## Search for documents within the last 7 days
    range_time = Q("range", **{"br_build_date_time": {"gte": start_date, "lt": end_date}})
    ## Search for documents where the total fail count >= 5
    more_than_one_failures = Q("range", **{"br_tests_object.br_summary_object.br_total_failed_count": {"gte": fail_count}})

    ## Filter out the test cases running between 162.38 and 320 seconds
    duration_between = Q("range", **{"br_tests_object.br_tests_failed_object.br_duration": {"gte": duration_low, "lte": duration_high}})

    # Combine them
    combined_filter = match_status & match_jobname & range_time & more_than_one_failures & duration_between

    # Setup aggregation
    test_agg = None
    if agg:
        test_agg = A('terms', field='br_tests_object.br_tests_failed_object.br_fullname.raw')

    result = make_query(index, combined_filter, includes=DETAILED_JOB['includes'], excludes=DETAILED_JOB['excludes'], size=size, agg=test_agg)
    return result

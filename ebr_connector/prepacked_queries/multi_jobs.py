"""
A collection of queries that provide multiple results as an array of dicts
"""

from elasticsearch_dsl import Q, A
from deprecated.sphinx import deprecated

from ebr_connector.schema.build_results import BuildResults
from ebr_connector.prepacked_queries import DEPRECATION_MESSAGE
from ebr_connector.prepacked_queries.query import make_query, DETAILED_JOB, JOB_MINIMAL


@deprecated(version="0.1.1", reason=DEPRECATION_MESSAGE)
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


@deprecated(version="0.1.1", reason=DEPRECATION_MESSAGE)
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
    ## Search for "failure", "FAILURE", "unstable", "UNSTABLE"
    match_status = Q("match", br_status_key=BuildResults.BuildStatus.FAILURE.name) | Q("match", br_status_key=BuildResults.BuildStatus.UNSTABLE.name)
    ## Search for documents within the last 7 days
    range_time = Q("range", **{"br_build_date_time": {"gte": start_date, "lt": end_date}})
    ## Search for documents where the total fail count >= 5
    more_than_one_failures = Q("range", **{"br_tests_object.br_summary_object.br_total_failed_count": {"gte": fail_count}})

    ## Filter out the test cases running between 162.38 and 320 seconds
    duration_between = Q("range", **{"br_tests_object.br_tests_failed_object.br_duration": {"gte": duration_low, "lte": duration_high}})

    # Combine them
    combined_filter = match_status & range_time & more_than_one_failures & duration_between

    if job_name:
        ## Search for the exact job name
        combined_filter &= Q("term", br_job_name__raw=job_name)

    # Setup aggregation
    test_agg = None
    if agg:
        test_agg = A('terms', field='br_tests_object.br_tests_failed_object.br_fullname.raw')

    return make_query(index, combined_filter, includes=DETAILED_JOB['includes'], excludes=DETAILED_JOB['excludes'], size=size, agg=test_agg)


@deprecated(version="0.1.1", reason=DEPRECATION_MESSAGE)
def job_matching_test(index, test_name, passed=True, failed=True, skipped=False, job_name=None, size=10, start_date="now-7d", end_date="now"):
    """
    Get information on a given test

    Args:
        index: Elastic search index to use
        test_name: Test name to look up, can include wildcards
        passed: Set to true to include passed tests while searching
        failed: Set to true to include failed tests while searching
        skipped: Set to true to include skipped tests while searching
        job_name: Job name to evaluate
        size: [Optional] Number of results to return. Default is 10.
        start_date: [Optional] Specify start date (string in elastic search format). Default is 7 days ago.
        end_date: [Optional] Specify end date (string in elastic search format). Default is now.
    Returns:
        An array of dicts of the matching information
    """
    # Over the specified time
    combined_filter = Q("range", **{"br_build_date_time": {"gte": start_date, "lt": end_date}})
    test_status_filter = None

    if passed:
        match_testname_passed = Q("wildcard", br_tests_object__br_tests_passed_object__br_fullname__raw=test_name)
        test_status_filter = match_testname_passed

    if failed:
        match_testname_failed = Q("wildcard", br_tests_object__br_tests_failed_object__br_fullname__raw=test_name)
        test_status_filter = match_testname_failed if not test_status_filter else test_status_filter | match_testname_failed

    if skipped:
        match_testname_skipped = Q("wildcard", br_tests_object__br_tests_skipped_object__br_fullname__raw=test_name)
        test_status_filter = match_testname_skipped if not test_status_filter else test_status_filter | match_testname_skipped

    if test_status_filter:
        combined_filter &= test_status_filter

    # Add job_name restriction of set
    if job_name:
        match_jobname = Q("term", br_job_name__raw=job_name)
        combined_filter &= match_jobname

    return make_query(index, combined_filter, includes=JOB_MINIMAL['includes'], excludes=JOB_MINIMAL['excludes'], size=size)


@deprecated(version="0.1.1", reason=DEPRECATION_MESSAGE)
def get_job(index, job_name, wildcard=False, size=10, start_date="now-7d", end_date="now"):
    """
    Get a list of all the builds recorded for a given job

    Args:
        index: Elastic search index to use
        job_name: Name of job to search within
        wildcard: When true, search with wildcard instead of exact match
    Returns:
        A list of the results from the job requested
    """
    search_type = "term"
    if wildcard:
        search_type = "wildcard"
    match_job_name = Q(search_type, br_job_name__raw=job_name)
    range_time = Q("range", **{"br_build_date_time": {"gte": start_date, "lt": end_date}})

    combined_filters = match_job_name & range_time

    return make_query(index, combined_filters, includes=DETAILED_JOB['includes'], excludes=DETAILED_JOB['excludes'], size=size)

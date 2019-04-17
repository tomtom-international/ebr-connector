from elasticsearch_dsl import Q, A

from ebr_connector.prepacked_queries.query import make_query
from ebr_connector.prepacked_queries.flaky_jobs import make_query

JOB_FIELDS = {
    "includes": [
        "br_build_date_time",
        "br_job_name",
        "br_job_info",
        "br_product",
        "br_build_id_key",
        "br_platform",
        "br_product_version_key",
        "br_tests_object.br_tests_failed_object.br_test",
        "br_tests_object.br_suites_object.br_package",
        "br_tests_object.br_tests_failed_object.br_classname",
        "br_tests_object.br_tests_failed_object.br_fullname",
        "br_tests_object.br_tests_failed_object.br_message",
        "br_tests_object.br_tests_failed_object.br_duration",
        "br_tests_object.br_tests_failed_object.br_reportset"
    ],
    "excludes": [
        "lhi*"
    ]
}

def get_failed_entries(index, start_date, end_date="now", collector=None, job_name=None):

    search_filters = Q("range", **{"br_build_date_time": {"gte": start_date, "lt": end_date}})

    if collector:
        # Filter for collector name
        search_filters &= Q("match", collector=collector)

    if job_name:
        # Filter for job name
        search_type = "wildcard" if "*" in job_name else "term"
        search_filters &= Q(search_type, br_job_name__raw=job_name)

    search_filters &= Q("range", **{"br_tests_object.br_summary_object.br_total_failed_count": {"gte": 1}})
    
    response = make_query(index, search_filters, size=100, includes=JOB_FIELDS['includes'], excludes=JOB_FIELDS['excludes'])

    return response

def create_dict_for_failed_test(failed_test, entry):

    failed_test_info = {}

    failed_test_info["status"] = "FAILED"
    failed_test_info["build_id"] = entry["br_build_id_key"]
    failed_test_info["product"] = entry["br_product"]
    failed_test_info["platform"] = entry["br_platform"]
    failed_test_info["job_name"] = entry["br_job_name"]
    failed_test_info["build_date"] = entry["br_build_date_time"]
    failed_test_info["build_version"] = entry["br_job_info"]
    failed_test_info["product_version"] = entry["br_product_version_key"]
    failed_test_info["test_name"] = failed_test["br_test"]
    failed_test_info["class_name"] = failed_test["br_classname"]
    failed_test_info["error_message"] = failed_test["br_message"]
    failed_test_info["duration"] = failed_test["br_duration"]
    failed_test_info["report_set"] = failed_test["br_reportset"]


    return failed_test_info


def get_failing_tests(index, start_date="now-7d", end_date="now", collector=None, job_name=None):

    response = get_failed_entries(index=index, start_date=start_date, end_date=end_date, collector=collector, job_name=job_name)
    failing_tests = []

    for entry in response:
        for failed_test in entry["br_tests_object"]["br_tests_failed_object"]:            
            failed_test_info = create_dict_for_failed_test(failed_test, entry)
            failing_tests.append(failed_test_info)
    #print("QUERY: %s" % (failing_tests))
    
    return failing_tests
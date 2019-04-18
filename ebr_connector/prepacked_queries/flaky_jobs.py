"""
A collection of queries that provide flaky test results
"""
from elasticsearch_dsl import Q, A

from ebr_connector.prepacked_queries.query import make_query

# The maximum number of records retrieved per query
MAXIMUM_NUM_RECORDS = 10000

# Provides most basic fields, for aggregated queries
AGG_FIELDS = {
    "includes": [
        "_id"
    ],
    "excludes": [
    ]
}

# Provides fields required for flaky analysis
JOB_FIELDS = {
    "includes": [
        "br_build_date_time",
        "br_job_name",
        "br_job_info",
        "br_build_id_key",
        "br_product_version_key",
        "br_tests_object.br_tests_failed_object.br_test",
        "br_tests_object.br_tests_failed_object.br_classname",
        "br_tests_object.br_tests_failed_object.br_reportset"
    ],
    "excludes": [
        "lhi*"
    ]
}

def get_dict_value(obj, key, default=None):
    """
    Get value of field in dictionary
    Args:
        obj: Dictionary containing value.
        key: Name of the field to retrieve.
        default: [Optional] Specify a default value, in case the field does not exist.
    Returns:
        The value of the field if it exists, or the default value
    """
    return obj[key] if key in obj else default

def calculate_flaky_score(num_passes, num_failures):
    """
    Calculate the flaky score of a test
    Args:
        num_passes: Number of times the test passed.
        num_failures: Number of times the test failed.
    Returns:
        The flaky score of the test (a percentage, where 100 is most flaky, and 0 is not flaky)
    """
    if num_passes + num_failures == 0:
        return 0
    return 200 * min(num_passes, num_failures) / (num_passes + num_failures)

def get_batches(index, start_date, end_date="now", collector=None, job_name=None, platform=None):
    """
    Get batches within date range
    Args:
        index: Elastic search index to use
        start_date: Specify start date (string in elastic search format).
        end_date: [Optional] Specify end date (string in elastic search format). Default is now.
        collector: [Optional] Collector name to use.
        job_name: [Optional] Job name to evaluate.
        platform: [Optional] Platform to evaluate.
    Returns:
        A dictionary of matching batches
    """

    def format_results(results):
        """
        Format aggregated results for batches into a dictionary of batches
        Args:
            results: Aggregated results for batches.
        Returns:
            A dictionary of batches
        """

        batches = {}
        num_entries = 0

        for build_version in results:
            job_names = {}
            for job in build_version.job_names.buckets:
                platforms = {}
                for platform in job.platforms.buckets:
                    build_ids = {}
                    for build_id in platform.build_ids.buckets:
                        entries = []
                        for entry_id in build_id.ids.buckets:
                            num_entries += 1
                            entry = {
                                "id": entry_id.key,
                                "num_failed_tests": entry_id.num_failed_tests.value,
                                "num_passed_tests": entry_id.num_passed_tests.value
                            }
                            entries.append(entry)
                        build_ids[build_id.key] = entries
                    platforms[platform.key] = build_ids
                job_names[job.key] = platforms
            batches[build_version.key] = job_names

        print("NUM ENTRIES: %d" % num_entries)
        return batches

    # Search for documents within the given range
    search_filters = Q("range", **{"br_build_date_time": {"gte": start_date, "lt": end_date}})

    if collector:
        # Filter for collector name
        search_filters &= Q("match", collector=collector)

    if job_name:
        # Filter for job name
        search_type = "wildcard" if "*" in job_name else "term"
        search_filters &= Q(search_type, br_job_name__raw=job_name)

    if platform:
        # Filter for platform
        search_type = "wildcard" if "*" in platform else "term"
        search_filters &= Q(search_type, br_platform__raw=platform)

    # Create aggregations to return number of batches
    agg = A("terms", field="br_job_info.raw", size=MAXIMUM_NUM_RECORDS)
    job_name_agg = A("terms", field="br_job_name.raw", size=MAXIMUM_NUM_RECORDS)
    platform_agg = A("terms", field="br_platform.raw", size=MAXIMUM_NUM_RECORDS)
    build_id_agg = A("terms", field="br_build_id_key", size=MAXIMUM_NUM_RECORDS)
    id_agg = A("terms", field="_id", size=MAXIMUM_NUM_RECORDS)

    # Nest the aggregations
    build_id_agg.bucket("ids", id_agg)
    platform_agg.bucket("build_ids", build_id_agg)
    job_name_agg.bucket("platforms", platform_agg)
    agg.bucket("job_names", job_name_agg)

    # Create metrics for number of failed/passed tests
    id_agg.metric("num_failed_tests", "sum", field="br_tests_object.br_summary_object.br_total_failed_count")
    id_agg.metric("num_passed_tests", "sum", field="br_tests_object.br_summary_object.br_total_passed_count")

    # Execute the query
    response = make_query(index, search_filters, agg=agg, size=None,
                          includes=AGG_FIELDS['includes'], excludes=AGG_FIELDS['excludes'])

    # Return the results, correctly formatted
    return format_results(response)

def get_entries_by_ids(index, ids, group_by=None):
    """
    Get entries by IDs
    Args:
        index: Elastic search index to use.
        ids: List of entry IDs.
        group_by: [Optional] Field to group entries by.
    Returns:
        An array of dicts of the matching entries
    """

    # Filter for IDs
    search_filters = Q("terms", _id=ids)

    # Execute the query
    response = make_query(index, search_filters, includes=JOB_FIELDS['includes'],
                          excludes=JOB_FIELDS['excludes'], size=MAXIMUM_NUM_RECORDS)

    print("Hits: %d" % len(response))

    if group_by:
        # Group results
        grouped_results = {}
        for entry in response:
            group_by_value = get_dict_value(entry, group_by)
            if group_by_value not in grouped_results:
                grouped_results[group_by_value] = []
            grouped_results[group_by_value].append(entry)
        return grouped_results

    return response

def get_number_of_times_test_passed_in_batch(index, ids, class_name, test_name):
    """
    Get the number of times a test passed in a given batch of entries
    Args:
        index: Elastic search index to use.
        ids: List of entry IDs.
        class_name: The class of the test.
        test_name: The name of the test.
    Returns:
        The number of times the test passed in the given entries
    """

    # Filter for IDs
    search_filters = Q("terms", _id=ids)

    # Filter for test
    fullname = "%s.%s" % (class_name, test_name)
    search_filters &= Q("match", br_tests_object__br_tests_passed_object__br_fullname__raw=fullname)

    agg = A("terms", field="_id", size=MAXIMUM_NUM_RECORDS)

    response = make_query(index, search_filters, includes=AGG_FIELDS['includes'],
                          excludes=AGG_FIELDS['excludes'], size=None, agg=agg)

    return len(response)

def create_flaky_data_for_test(class_name, test_name, num_passes, num_failures, num_skipped, num_runs, report_set):
    """
    Creates a dictionary of flaky data for one test
    Args:
        class_name: The class of the test.
        test_name: The name of the test.
        num_passes: Number of times the test passed.
        num_failures: Number of times the test failed.
        num_skipped: Number of times the test skipped.
        num_runs: Number of times the test was run.
        report_set: The report set of the test.
    Returns:
        A dictionary of flaky data for one test
    """

    flaky_data_for_test = {
        "class_name": class_name,
        "test_name": test_name,
        "report_set": report_set,
        "num_passes": num_passes,
        "num_failures": num_failures,
        "num_skipped": num_skipped,
        "num_runs": num_runs,
        "flaky_score": calculate_flaky_score(num_passes, num_failures),
    }

    return flaky_data_for_test

def set_test_result_in_flaky_data(flaky_data_for_test, num_passes=None, num_failures=None, num_skipped=None):
    """
    Updates the flaky data for one test
    Args:
        flaky_data_for_test: The dictionary of flaky data for one test to update.
        num_passes: [Optional] Number of times the test passed.
        num_failures: [Optional] Number of times the test failed.
        num_skipped: [Optional] Number of times the test skipped.
    """

    recalculate_flaky_score = False

    # Update the figures in the data
    if num_passes is not None:
        flaky_data_for_test["num_passes"] = num_passes
        recalculate_flaky_score = True
    if num_failures is not None:
        flaky_data_for_test["num_failures"] = num_failures
        recalculate_flaky_score = True
    if num_skipped is not None:
        flaky_data_for_test["num_skipped"] = num_skipped

    # Recalculate the flaky score
    if recalculate_flaky_score:
        flaky_data_for_test["flaky_score"] = calculate_flaky_score(flaky_data_for_test["num_passes"],
                                                                   flaky_data_for_test["num_failures"])

def add_failing_test_to_flaky_data(num_runs, flaky_data, test):
    """
    Adds a failing test to the flaky data for a batch
    Args:
        num_runs: Number of runs in the batch.
        flaky_data: The dictionary of flaky data for the batch to update.
        test: The test result.
    """

    class_name = get_dict_value(test, "br_classname", "none")
    test_name = get_dict_value(test, "br_test", "none")
    report_set = get_dict_value(test, "br_reportset", "")

    # If the test has no flaky data yet, create a placeholder for it
    if class_name not in flaky_data:
        flaky_data[class_name] = {}
    if test_name not in flaky_data[class_name]:
        flaky_data[class_name][test_name] \
            = create_flaky_data_for_test(class_name, test_name, 0, 0, 0, num_runs, report_set)

    flaky_data_for_test = flaky_data[class_name][test_name]

    if report_set != flaky_data_for_test["report_set"]:
        raise Exception("Report set changed!")

    # Increment the number of times this test has failed
    set_test_result_in_flaky_data(flaky_data_for_test, num_failures=flaky_data_for_test["num_failures"] + 1)

def get_flaky_data_for_entry(entry, num_runs, flaky_data):
    """
    Gets the flaky analysis data for one entry
    Args:
        entry: The database entry.
        num_runs: Number of runs in the batch.
        flaky_data: The dictionary of flaky data for the batch to update.
    """

    # We ignore situations where there are not multiple runs
    if num_runs <= 1:
        return

    # Get data from the entry
    build_id = get_dict_value(entry, "br_build_id_key")
    build_date_time = get_dict_value(entry, "br_build_date_time", "")
    product_version = get_dict_value(entry, "br_product_version_key", "")
    tests_object = get_dict_value(entry, "br_tests_object", {})

    # Update data for this batch and build
    flaky_data["batch"]["product_version"] = product_version
    flaky_data["builds"][build_id]["build_date_time"] = build_date_time

    # Get all failing tests
    failing_tests = get_dict_value(tests_object, "br_tests_failed_object", [])

    # Iterate through all failing tests and collect flaky data for each
    for failing_test in failing_tests:
        add_failing_test_to_flaky_data(num_runs, flaky_data["tests"], failing_test)

def update_flaky_data_for_test(flaky_data_for_test, class_name, test_name, index, entry_ids, num_runs):
    """
    Updates the flaky analysis data for one test, by retrieving the number of times the test passed
    Args:
        flaky_data_for_test: The dictionary of flaky data for one test to update.
        class_name: The class of the test.
        test_name: The name of the test.
        index: Elastic search index to use
        entry_ids: List of entry IDs.
        num_runs: Number of runs in the batch.
    Returns:
        True if the test is flaky, False otherwise
    """

    # If there are no failures for this test, or all tests failed, it is not flaky and we exclude it
    num_failures = flaky_data_for_test["num_failures"]
    if not num_failures or num_failures == num_runs:
        return False

    num_passes = get_number_of_times_test_passed_in_batch(index, entry_ids, class_name, test_name)

    # If there are no passes for this test it is not flaky and we exclude it
    if not num_passes:
        return False

    # Update the figures in the data
    set_test_result_in_flaky_data(flaky_data_for_test, num_passes=num_passes,
                                  num_skipped=num_runs - num_passes - num_failures)

    print("NUM RUNS: %d, NUM PASSES: %d, NUM FAILURES: %d, CLASS: %s, TEST: %s" %
          (num_runs, num_passes, num_failures, class_name, test_name))

    return True

def get_flaky_data_for_batch(runs_in_batch, build_version, job_name, platform, num_runs, index, entry_ids):
    """
    Gets the flaky analysis data for one batch
    Args:
        runs_in_batch: The dictionary of entries for the batch.
        build_version: The build version of the batch.
        job_name: The job name of the batch.
        platform: The platform of the batch.
        num_runs: Number of runs in the batch.
        index: Elastic search index to use
        entry_ids: List of entry IDs.
    Returns:
        A dictionary of flaky data for one batch
    """

    flaky_data = {
        "batch": {
            "build_version": build_version,
            "job_name": job_name,
            "platform": platform
        },
        "builds": {},
        "tests": {}
    }

    # Iterate through all entries in the runs for the batch and set the number of failures
    for build_id in runs_in_batch:
        entries = runs_in_batch[build_id]

        flaky_data["builds"][build_id] = {
            "build_id": build_id
        }

        for entry in entries:
            get_flaky_data_for_entry(entry, num_runs, flaky_data)

    # Iterate through the results for this batch and set the number of passes
    for class_name in flaky_data["tests"]:
        for test_name in flaky_data["tests"][class_name]:
            flaky_data_for_test = flaky_data["tests"][class_name][test_name]

            test_is_flaky = update_flaky_data_for_test(flaky_data_for_test, class_name, test_name, index, entry_ids,
                                                       num_runs)
            if not test_is_flaky:
                # This test is not flaky, so we exclude it
                flaky_data["tests"][class_name][test_name] = None

    return flaky_data

def get_entry_ids_for_batch(batch):
    """
    Gets the entry IDs for the given batch
    Args:
        batch: The batch dictionary.
    Returns:
        Number of runs in the batch
        A list of IDs of all entries in the batch
        A list of IDs of failing entries in the batch
    """

    entry_ids = []
    failed_ids = []

    num_runs = len(batch)
    if num_runs < 2:
        # A valid batch must have multiple runs
        return 0, [], []

    # Find all the entries within this batch
    for build_id in batch:
        for entry in batch[build_id]:
            entry_id = entry["id"]
            if entry["num_failed_tests"] > 0:
                failed_ids.append(entry_id)
                entry_ids.append(entry_id)
            elif entry["num_passed_tests"] > 0:
                entry_ids.append(entry_id)

    if not entry_ids or not failed_ids:
        # This batch has no failed entries
        return 0, [], []

    return num_runs, entry_ids, failed_ids

def add_flaky_data_for_batch(flaky_data_for_batch, flaky_tests):
    """
    Adds the given flaky data for one batch to the flaky test data
    Args:
        flaky_data_for_batch: The dictionary of flaky data for one batch.
        flaky_tests: The dictionary of flaky test data to update.
    """

    # Iterate through the results for this batch and add to the global list of flaky tests
    for class_name in flaky_data_for_batch["tests"]:
        for test_name in flaky_data_for_batch["tests"][class_name]:

            flaky_data_for_test = flaky_data_for_batch["tests"][class_name][test_name]

            if not flaky_data_for_test:
                # There is no data for this test
                continue

            # Add all values from batch data
            for key in flaky_data_for_batch["batch"]:
                flaky_data_for_test[key] = flaky_data_for_batch["batch"][key]

            # Add all values from builds data
            flaky_data_for_test["builds"] = []
            for build_id in flaky_data_for_batch["builds"]:
                build_obj = {}
                for key in flaky_data_for_batch["builds"][build_id]:
                    build_obj[key] = flaky_data_for_batch["builds"][build_id][key]
                flaky_data_for_test["builds"].append(build_obj)

            # Add the data for this test to the global list
            if class_name not in flaky_tests:
                flaky_tests[class_name] = {}
            if test_name not in flaky_tests[class_name]:
                flaky_tests[class_name][test_name] = []
            flaky_tests[class_name][test_name].append(flaky_data_for_test)

def get_flaky_data_for_batches(index, batches):
    """
    Returns the flaky analysis data for the given batches
    Args:
        index: Elastic search index to use
        batches: Dictionary of batches.
    Returns:
        Dictionary of flaky test data, grouped by class name then test name
    """

    flaky_tests = {}

    # Iterate through all batches and get the flaky data for each
    for build_version in batches:
        for job_name in batches[build_version]:
            for platform in batches[build_version][job_name]:
                batch = batches[build_version][job_name][platform]

                num_runs, entry_ids, failed_ids = get_entry_ids_for_batch(batch)

                if not num_runs:
                    # This is not a valid batch
                    continue

                print("%s, %s, %s (%d runs) (%d entries)" % (build_version, job_name, platform, num_runs, len(entry_ids)))

                # Get the entries that have failed, grouped by build ID
                failed_runs_in_batch = get_entries_by_ids(index=index, ids=failed_ids, group_by="br_build_id_key")

                # Get the flaky data for this batch
                flaky_data_for_batch = get_flaky_data_for_batch(failed_runs_in_batch, build_version, job_name, platform,
                                                                num_runs, index, entry_ids)

                # Add results for this batch to the global list of flaky tests
                add_flaky_data_for_batch(flaky_data_for_batch, flaky_tests)

    return flaky_tests

def get_flaky_tests(index, start_date, end_date="now", collector=None, job_name=None, platform=None):
    """
    Returns the flaky analysis data for the given parameters
    Args:
        index: Elastic search index to use
        start_date: Specify start date (string in elastic search format).
        end_date: [Optional] Specify end date (string in elastic search format). Default is now.
        collector: [Optional] Collector name to use.
        job_name: [Optional] Job name to evaluate.
        platform: [Optional] Platform to evaluate.
    Returns:
        Dictionary of flaky test data, grouped by class name then test name
    """

    # Get all batches of flaky tests
    batches = get_batches(index=index, start_date=start_date, end_date=end_date, collector=collector,
                          job_name=job_name, platform=platform)

    # Get the flaky data for all batches
    return get_flaky_data_for_batches(index, batches)

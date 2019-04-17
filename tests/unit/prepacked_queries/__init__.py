"""Module providing test data for flaky test queries.
"""
from unittest.mock import MagicMock

MOCK_JOBS_DATA = {
    "id1": {
        "br_build_date_time": "2019-04-16T22:03:41",
        "br_job_name": "jobname1",
        "br_job_info": "buildversion1",
        "br_platform": "platform1",
        "br_build_id_key": "buildid1",
        "br_product_version_key": "productversion1",
        "br_tests_object": {
            "br_tests_failed_object": [{
                "br_test": "test1",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            },{
                "br_test": "test2",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }],
            "br_tests_passed_object": [{
                "br_test": "test3",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }]
        }
    },
    "id2": {
        "br_build_date_time": "2019-04-16T22:03:42",
        "br_job_name": "jobname1",
        "br_job_info": "buildversion1",
        "br_platform": "platform1",
        "br_build_id_key": "buildid1",
        "br_product_version_key": "productversion1",
        "br_tests_object": {
            "br_tests_passed_object": [{
                "br_test": "test1",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            },{
                "br_test": "test2",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }]
        }
    },
    "id3": {
        "br_build_date_time": "2019-04-16T22:03:43",
        "br_job_name": "jobname1",
        "br_job_info": "buildversion1",
        "br_platform": "platform1",
        "br_build_id_key": "buildid2",
        "br_product_version_key": "productversion1",
        "br_tests_object": {
            "br_tests_passed_object": [{
                "br_test": "test1",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }]
        }
    },
    "id4": {
        "br_build_date_time": "2019-04-16T22:03:44",
        "br_job_name": "jobname1",
        "br_job_info": "buildversion1",
        "br_platform": "platform1",
        "br_build_id_key": "buildid2",
        "br_product_version_key": "productversion1",
        "br_tests_object": {
            "br_tests_failed_object": [{
                "br_test": "test1",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }, {
                "br_test": "test2",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }, {
                "br_test": "test3",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }, {
                "br_test": "test4",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }],
            "br_tests_passed_object": [{
                "br_test": "test5",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }, {
                "br_test": "test6",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }]
        }
    },
    "id5": {
        "br_build_date_time": "2019-04-16T22:03:45",
        "br_job_name": "jobname1",
        "br_platform": "platform2",
        "br_job_info": "buildversion1",
        "br_build_id_key": "buildid1",
        "br_product_version_key": "productversion1",
        "br_tests_object": {
            "br_tests_failed_object": [{
                "br_test": "test1",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }],
            "br_tests_passed_object": [{
                "br_test": "test2",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }, {
                "br_test": "test3",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }]
        }
    },
    "id6": {
        "br_build_date_time": "2019-04-16T22:03:46",
        "br_job_name": "jobname1",
        "br_job_info": "buildversion1",
        "br_platform": "platform2",
        "br_build_id_key": "buildid2",
        "br_product_version_key": "productversion1",
        "br_tests_object": {
            "br_tests_failed_object": [{
                "br_test": "test1",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }, {
                "br_test": "test2",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }, {
                "br_test": "test3",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }],
            "br_tests_passed_object": [{
                "br_test": "test4",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }]
        }
    },
    "id7": {
        "br_build_date_time": "2019-04-16T22:03:47",
        "br_job_name": "jobname2",
        "br_job_info": "buildversion1",
        "br_platform": "platform1",
        "br_build_id_key": "buildid1",
        "br_product_version_key": "productversion1"
    },
    "id8": {
        "br_build_date_time": "2019-04-16T22:03:48",
        "br_job_name": "jobname2",
        "br_job_info": "buildversion1",
        "br_platform": "platform1",
        "br_build_id_key": "buildid2",
        "br_product_version_key": "productversion1",
        "br_tests_object": {
            "br_tests_failed_object": [{
                "br_test": "test1",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }, {
                "br_test": "test2",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }, {
                "br_test": "test3",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }, {
                "br_test": "test4",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }],
            "br_tests_passed_object": [{
                "br_test": "test5",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }, {
                "br_test": "test6",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }]
        }
    },
    "id9": {
        "br_build_date_time": "2019-04-16T22:03:49",
        "br_job_name": "jobname2",
        "br_job_info": "buildversion1",
        "br_platform": "platform2",
        "br_build_id_key": "buildid1",
        "br_product_version_key": "productversion1",
        "br_tests_object": {
            "br_tests_failed_object": [{
                "br_test": "test1",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }, {
                "br_test": "test2",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }],
            "br_tests_passed_object": [{
                "br_test": "test3",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }, {
                "br_test": "test4",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }]
        }
    },
    "id10": {
        "br_build_date_time": "2019-04-16T22:03:50",
        "br_job_name": "jobname2",
        "br_job_info": "buildversion1",
        "br_platform": "platform2",
        "br_build_id_key": "buildid2",
        "br_product_version_key": "productversion1",
        "br_tests_object": {
            "br_tests_failed_object": [{
                "br_test": "test1",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }, {
                "br_test": "test2",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }],
            "br_tests_passed_object": [{
                "br_test": "test3",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }, {
                "br_test": "test4",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }, {
                "br_test": "test5",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }, {
                "br_test": "test6",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }]
        }
    },
    "id11": {
        "br_build_date_time": "2019-04-16T22:03:51",
        "br_job_name": "jobname1",
        "br_job_info": "buildversion2",
        "br_platform": "platform1",
        "br_build_id_key": "buildid1",
        "br_product_version_key": "productversion1",
        "br_tests_object": {
            "br_tests_failed_object": [{
                "br_test": "test1",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }, {
                "br_test": "test2",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }],
            "br_tests_passed_object": [{
                "br_test": "test3",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }]
        }
    },
    "id12": {
        "br_build_date_time": "2019-04-16T22:03:52",
        "br_job_name": "jobname1",
        "br_job_info": "buildversion2",
        "br_platform": "platform1",
        "br_build_id_key": "buildid2",
        "br_product_version_key": "productversion1",
        "br_tests_object": {
            "br_tests_failed_object": [{
                "br_test": "test1",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }, {
                "br_test": "test2",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }, {
                "br_test": "test3",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }],
            "br_tests_passed_object": [{
                "br_test": "test4",
                "br_classname": "class1",
                "br_reportset": "reportset1"
            }]
        }
    }
}


def _format_results_data(results_data):
    hits = []
    for result in results_data:
        hit = {
            "_source": result
        }
        hits.append(hit)

    response = {
        "hits": {
            "hits": hits
        }
    }
    return response

def _format_aggregation_data(aggregation_data):
    response = {
        "aggregations": {
            "fail_count": {
                "buckets": aggregation_data
            }
        }
    }
    return response

def _format_batch_data(batch_data):

    build_versions = []
    for build_version_key in batch_data:
        build_version = MagicMock()
        build_version.key = build_version_key
        build_version.job_names = MagicMock()

        job_names = []
        for job_name_key in batch_data[build_version_key]:
            job_name = MagicMock()
            job_name.key = job_name_key
            job_name.platforms = MagicMock()

            platforms = []
            for platform_key in batch_data[build_version_key][job_name_key]:
                platform = MagicMock()
                platform.key = platform_key
                platform.build_ids = MagicMock()

                build_ids = []
                for build_id_key in batch_data[build_version_key][job_name_key][platform_key]:
                    build_id = MagicMock()
                    build_id.key = build_id_key
                    build_id.ids = MagicMock()

                    entry_ids = []
                    for id_key in batch_data[build_version_key][job_name_key][platform_key][build_id_key]:
                        entry_id = MagicMock()
                        entry_id.key = id_key

                        id_data = batch_data[build_version_key][job_name_key][platform_key][build_id_key][id_key]
                        entry_id.num_failed_tests = MagicMock()
                        entry_id.num_failed_tests.value = id_data["num_failed_tests"]
                        entry_id.num_passed_tests = MagicMock()
                        entry_id.num_passed_tests.value = id_data["num_passed_tests"]

                        entry_ids.append(entry_id)

                    build_id.ids.buckets = entry_ids
                    build_ids.append(build_id)

                platform.build_ids.buckets = build_ids
                platforms.append(platform)

            job_name.platforms.buckets = platforms
            job_names.append(job_name)

        build_version.job_names.buckets = job_names
        build_versions.append(build_version)

    return build_versions

def _get_results_for_ids(entry_ids, jobs_data):
    results_data = []

    for entry_id in entry_ids:
        results_data.append(jobs_data[entry_id])

    return results_data

def _create_batch_data(jobs_data):
    batch_data = {}

    for entry_id in jobs_data:
        entry = jobs_data[entry_id]
        build_version = entry["br_job_info"]
        job_name = entry["br_job_name"]
        platform = entry["br_platform"]
        build_id = entry["br_build_id_key"]
        tests_object = entry.get("br_tests_object", {})

        if build_version not in batch_data:
            batch_data[build_version] = {}
        if job_name not in batch_data[build_version]:
            batch_data[build_version][job_name] = {}
        if platform not in batch_data[build_version][job_name]:
            batch_data[build_version][job_name][platform] = {}
        if build_id not in batch_data[build_version][job_name][platform]:
            batch_data[build_version][job_name][platform][build_id] = {}
        if entry_id not in batch_data[build_version][job_name][platform][build_id]:
            batch_data[build_version][job_name][platform][build_id][entry_id] = {}

        batch_data[build_version][job_name][platform][build_id][entry_id]["num_failed_tests"] \
            = len(tests_object.get("br_tests_failed_object", []))
        batch_data[build_version][job_name][platform][build_id][entry_id]["num_passed_tests"] \
            = len(tests_object.get("br_tests_passed_object", []))

    return batch_data

def _get_num_passes_data(num_passes):
    data = {}
    for index in range(0, num_passes):
        data["id%d" % (index+1)] = {}
    return _format_aggregation_data(data)

def _get_num_passes_for_test(class_name, test_name, entry_ids, jobs_data):
    num_passes = 0

    for entry_id in entry_ids:
        entry = jobs_data[entry_id]
        tests_object = entry.get("br_tests_object", {})
        tests_passed_object = tests_object.get("br_tests_passed_object", [])

        for test in tests_passed_object:
            if test.get("br_classname", "") == class_name and test.get("br_test", "") == test_name:
                num_passes += 1

    return num_passes

def get_batch_data(jobs_data=MOCK_JOBS_DATA):
    return _format_aggregation_data(_format_batch_data(_create_batch_data(jobs_data)))

def get_results_data_for_ids(entry_ids, jobs_data=MOCK_JOBS_DATA):
    return _format_results_data(_get_results_for_ids(entry_ids, jobs_data))

def get_num_passes_data_for_test(class_name, test_name, entry_ids, jobs_data=MOCK_JOBS_DATA):
    return _get_num_passes_data(_get_num_passes_for_test(class_name, test_name, entry_ids, jobs_data))

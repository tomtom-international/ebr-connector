# -*- coding: utf-8 -*-

"""
Library with convience functions for use in hooks
"""

import argparse
from datetime import datetime
import requests


from ebr_connector.schema.build_results import BuildResults
from ebr_connector.hooks.common.args import add_common_args, add_build_args, validate_args


def parse_args(description, custom_args=None):
    """
    Performs default arg parsing for a hook

    Args:
        description: description to provide for the hook CLI
        custom_args: (optional) callback with any arguments unique to the hook
    """
    parser = argparse.ArgumentParser(description=description)
    add_common_args(parser)
    add_build_args(parser)
    if custom_args:
        custom_args(parser)
    args = parser.parse_args()
    validate_args(args)

    return args


def status_args(build_status):
    """
    Callback function to provide the build status from parsed commandline args to :class:`ebr_connector.schema.BuildResults`

    Args:
        args: argparse'd arguments that include the build status
    """
    return BuildResults.BuildStatus.create(build_status).name


def assemble_build(args, retrieve_function, retrieve_args):
    """
    Provides a CLI interface to send build results to Elasticsearch
    Requires a callback function for retrieving tests, but gets the status from command line arguments.

    Args:
        args: argparse'd arguments
        retrieve_function: call back argument to decode retrieve and decode tests
        retrieve_args: arguments to the retrieve_function callback
    """
    job_info = get_json_job_details(args.buildurl)
    job_name = job_info["fullName"]

    build_info = get_json_job_details(args.buildurl + "/" + args.buildid)
    build_date_time = datetime.utcfromtimestamp(int(build_info["timestamp"])/1000).isoformat()
    build_job_url = build_info["url"]

    build_results = BuildResults.create(job_name=job_name, build_id=args.buildid, build_date_time=build_date_time,
                                        job_link=build_job_url, platform=args.platform,
                                        product_version=args.productversion)
    build_results.store_tests(retrieve_function, *retrieve_args)
    build_results.store_status(status_args, build_info["result"])

    return build_results


def normalize_string(value):
    """Some parameterized tests encode the parameter objects into the test case name. For classes that have a
    proper output operator << implemented this is not an issue but classes without one produce a large test
    case with some byte object representation.

    Some examples how such test case names look like:

    .. code-block:: none

        ShapePointsTest/0 (lat = 51.8983, lon = 19.5026)
        GatewayTwinLinksQuantityTest/0 (16-byte object <60-A5 DE-03 00-00 00-00 02-00 02-00 00-00 00-00>)
        TestPassageRestrictions/0 (TestData: testPoint(44.6553, 7.38968)   Handle:               0\n

    We do not allow this and clean this up by removing everything after ` (`) and store only the real test case
    name and the index of the parameterized test.

    Args:
        value: String to be normalized
    """
    if value is None:
        return ""
    head, _, _ = value.partition(" (")
    return head.strip()


def get_json_job_details(buildurl):
    """Returns detailed information in JSON about a job/build/etc. depending on the passed URL.
    """
    return requests.get(buildurl + "/api/json").json()

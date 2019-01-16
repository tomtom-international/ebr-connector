# -*- coding: utf-8 -*-

"""
Library with convience functions for use in hooks
"""

import argparse


from elastic.schema.build_results import BuildResults
from elastic.hooks.common.args import add_common_args, add_build_args, validate_args

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

def status_args(args):
    """
    Callback function to provide the build status from parsed commandline args to :class:`elastic.schema.BuildResults`

    Args:
        args: argparse'd arguments that include the build status
    """
    return BuildResults.BuildStatus.create(args.buildstatus).name

def assemble_build(args, retrieve_function, retrieve_args):
    """
    Provides a CLI interface to send build results to logstash
    Requires a callback function for retrieving tests, but gets the status from command line arguments.

    Args:
        args: argparse'd arguments
        retrieve_function: call back argument to decode retrieve and decode tests
        retrieve_args: arguments to the retrieve_function callback
    """
    build_results = BuildResults.create(job_name=args.jobname, build_id=args.buildid, build_date_time=args.buildtime,
                                        job_link=args.buildurl, platform=args.platform)
    build_results.store_tests(retrieve_function, *retrieve_args)
    build_results.store_status(status_args, args)

    return build_results

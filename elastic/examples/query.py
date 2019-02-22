#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Example how to query ElasticSearch for test reports.
"""


import argparse
from getpass import getpass
import json
import sys
import urllib
from elasticsearch_dsl import connections, Q
from elastic.schema.build_results import BuildResults


def main():
    """Main entrypoint for example script querying ElasticSearch.
    """

    parser = argparse.ArgumentParser(description="Script runnig several example queries against Elasticsearch.")
    parser.add_argument("--host", default="localhost", help="[Optional] Elasticsearch host to connect to (default: localhost)")
    parser.add_argument("--port", default=9200, help="[Optional] Elasticsearch port to connect to (default: 9200)")
    parser.add_argument("--cacert", help="[Optional] CA cert file in PEM format (if required)")
    parser.add_argument("--user", default="elastic", help="[Optional] User account to bind to (default: elastic)")
    parser.add_argument("--password", default=None, help="[Optional] Password for user account to bind to (default: None)")
    parser.add_argument("--index", default="staging*", help="[Optional] Name of Elasticsearch index (default: staging*)")
    args = parser.parse_args()

    if not args.password and args.user:
        args.password = getpass("Password for " + args.user + ": ")

    # URL encode the user and password to enable it to used with HTTP BASIC auth safely
    enc_user = urllib.parse.quote_plus(args.user)
    enc_password = urllib.parse.quote_plus(args.password)

    # Create default connection to Elasticsearch instance
    connections.create_connection(
        hosts=[{
            "host":  args.host,
            "http_auth": enc_user + ":" + enc_password,
            "port": args.port,
            "timeout": 20,
            "use_ssl": bool(args.cacert),
            "verify_certs": bool(args.cacert),
            "ca_certs": args.cacert
        }])

    query_failed_tests(args.index)
    query_for_successful_job(args.index)


def query_for_successful_job(index):
    """Queries for successful tests
    """

    # Create a Search API object
    search = BuildResults().search(index=index)

    # Create some filters
    ## Search for all jobs that fullfil the regex. The regex is evaluated on the keyword field (`raw`) of the field `br_job_name`.
    match_jobname = Q("regexp", br_job_name__raw="cpp-reflection-tests-BB.*PR-.*")
    ## and have the following build status
    match_status = Q("match", br_status_key=BuildResults.BuildStatus.SUCCESS.name)
    # within the specified range
    range_time = Q("range", **{"br_build_date_time": {"gte": "now-7d", "lt": "now"}})

    # Combine them
    combined_filter = match_jobname & match_status & range_time

    # Create a query with limited fields and ...
    search = search.source(
        includes=[
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
        excludes=["lhi*"])

    # combined filters
    search = search.query("bool", filter=[combined_filter])[0:1] # pylint: disable=no-member

    dump_formatted(search)

    response = search.execute()
    dump_formatted(response)

    # Iterate over the search results
    for hit in response:
        dump_formatted(hit)
    print("Hits: %d" % search.count())

    return response


def query_failed_tests(index):
    """Queries for failed tests
    """

    # Create a Search API object
    search = BuildResults().search(index=index)

    # Create some filters
    ## Search for the exact job name
    match_jobname = Q("term",
                      br_job_name__raw="cpp-reflection-tests-BB-baseline")
    ## Search for "failure", "FAILURE", "unstable", "UNSTABLE"
    match_status = Q("match", br_status_key=BuildResults.BuildStatus.FAILURE.name) | Q("match", br_status_key=BuildResults.BuildStatus.UNSTABLE.name)
    ## Search for documents within the last 7 days
    range_time = Q("range", **{"br_build_date_time": {"gte": "now-7d", "lt": "now"}})
    ## Search for documents where the total fail count >= 5
    more_than_one_failures = Q("range", **{"br_tests_object.br_summary_object.br_total_failed_count": {"gte": 5}})

    ## Filter out the test cases running between 162.38 and 320 seconds
    duration_between = Q("range", **{"br_tests_object.br_tests_failed_object.br_duration": {"gte": 162.38, "lte": 320}})

    # Combine them
    combined_filter = match_status & match_jobname & range_time & more_than_one_failures & duration_between

    # Create a query with limited fields and ...
    search = search.source(
        includes=[
            "br_job_name",
            "br_build_date_time",
            "br_job_url_key",
            "br_source",
            "br_build_id_key",
            "br_platform",
            "br_product",
            "br_status_key",
            "br_version_key",
            "br_tests_object.br_tests_failed_object"
        ],
        excludes=["lhi*"])

    # combined filters
    search = search.query("bool", filter=[combined_filter])[0:1] # pylint: disable=no-member

    dump_formatted(search)

    # Execute the query
    response = search.execute()
    dump_formatted(response)

    # Iterate over the response and print only the hits
    for hit in response:
        dump_formatted(hit)
    print("Hits: %d" % len(response))

    return response


def dump_formatted(json_value):
    """Dump the json value formatted on the console.
    """
    print(json.dumps(json_value.to_dict(), indent=2, sort_keys=True, default=str))

if __name__ == '__main__':
    sys.exit(main())

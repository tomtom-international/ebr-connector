#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Example how to query ElasticSearch for test reports.
"""


import argparse
from getpass import getpass
import json
import sys
import urllib
from elasticsearch_dsl import connections
from ebr_connector.prepacked_queries.multi_jobs import successful_jobs, failed_tests


def main():
    """Main entrypoint for example script querying ElasticSearch.
    """

    parser = argparse.ArgumentParser(description="Script runnig several example queries against Elasticsearch.")
    parser.add_argument("--host", default="localhost", help="[Optional] Elasticsearch host to connect to (default: localhost)")
    parser.add_argument("--port", default=9200, help="[Optional] Elasticsearch port to connect to (default: 9200)")
    parser.add_argument("--cacert", help="[Optional] CA cert file in PEM format (if required)")
    parser.add_argument("--ssl", default=True, type=bool, help="[Optional] Set to false to use plaintext HTTP")
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
            "use_ssl": args.ssl,
            "verify_certs": bool(args.cacert),
            "ca_certs": args.cacert
        }])

    query_failed_tests(args.index)
    query_for_successful_job(args.index)


def query_for_successful_job(index):
    """Queries for successful tests
    """
    response = successful_jobs(index, "cpp-reflection-tests-BB.*PR-.*", size=5)

    # Iterate over the search results
    for hit in response:
        dump_formatted(hit)
    print("Hits: %d" % len(response))

    return response


def query_failed_tests(index):
    """Queries for failed tests
    """
    response = failed_tests(index, job_name="cpp-reflection-tests-BB-baseline", size=5)

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

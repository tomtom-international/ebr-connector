# -*- coding: utf-8 -*-

"""
Module with common argparser configuration for hooks
"""

import ebr_connector


def add_common_args(parser):
    """
    Common argparser configuration for hooks

    Args:
        parser: Args parser object
    """
    parser.add_argument("-b", "--buildid", type=str, required=True, help="CI build ID")
    parser.add_argument("-j", "--jobname", type=str, help="CI job name")
    parser.add_argument("-p", "--platform", type=str, default="Linux-x86_64", help="Platform name (default: Linux-x86_64)")
    parser.add_argument("-v", "--productversion", type=str, help="Product version")

    parser.add_argument("--logcollectaddr", type=str, required=True, help="Address of LogCollector to send to")
    parser.add_argument("--logcollectport", type=int, required=True, help="Port on the LogCollector to send to")
    parser.add_argument("--sockettimeout", type=int, default=10, help="Socket timeout in seconds for the write operation (default: 10)")
    parser.add_argument("--cacert", default=None, help="Location of CA cert to verify against.")
    parser.add_argument("--clientcert", default=None, help="Client certificate file. Must also provide client key.")
    parser.add_argument("--clientkey", default=None, help="Client key file. Must also provide client certificate.")
    parser.add_argument("--clientpassword", default="", help="Client key file's password. Only use if there is a password on the keyfile.")
    parser.add_argument("--version", action="version", version=ebr_connector.__version__)


def add_build_args(parser):
    """
    Common (not required) build arguments for hooks

    Args:
        parser: Args parser object
    """
    parser.add_argument('--buildurl', required=True, help='URL of build to send')


def validate_args(args):
    """
    Performs validation of common arguments provided to hooks.
    Currently only checks if key and certificate are both provided if either are.

    Args:
        args: arguments parsed from argparser object
    """
    if (args.clientcert or args.clientkey) and not (args.clientcert and args.clientkey):
        print("Either both '--clientcert' and '--clientkey' must be set or neither should be set.")
        exit(1)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

def addCommonArgs(parser):
    parser.add_argument("-b", "--buildid", type=str, required=True, help="CI build ID")
    parser.add_argument("-j", "--jobname", type=str, default=None, help="CI Job name")
    parser.add_argument("-p", "--platform", type=str, default="linux", help="Platform name (default: linux)")

    parser.add_argument("--logcollectaddr", type=str, required=True, help="Address of LogCollector to send to")
    parser.add_argument("--logcollectport", type=int, required=True, help="Port on the LogCollector to send to")
    parser.add_argument("--cacert", default=None, help="Location of CA cert to verify against.")
    parser.add_argument("--clientcert", default=None, help="Client certificate file. Must also provide client key.")
    parser.add_argument("--clientkey", default=None, help="Client key file. Must also provide client certificate.")
    parser.add_argument("--clientpassword", default="", help="Client key file's password. Only use if there is a password on the keyfile.")

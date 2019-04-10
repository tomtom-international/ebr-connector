#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generates an index template for ElasticSearch from the BuildResults document.
"""

import argparse
import json
import sys

from elasticsearch_dsl import Index
from ebr_connector.schema.build_results import _BuildResultsMetaDocument


def generate_template(index_name):
    """
    Generates the index template associated with the structure of the BuildResults
    document, allowing it to be uploaded to an ElasticSearch instance.

    Args:
        index_name: index name to generate the template with, should be the index the module will upload to
        output_file: (optional) file path to write template to
    """

    document = _BuildResultsMetaDocument()
    index = Index(name=index_name)
    index.document(document)
    index.settings(
        refresh_interval="30s",
        number_of_shards="1",
        number_of_replicas="1"
    )
    index.aliases(**{index_name: {}})
    index_template = index.as_template(template_name="template_" + index_name, pattern="%s-*" % index_name)
    return index_template.to_dict()



def main():
    """
    CLI interface to generate the index template for BuildResults
    """
    parser = argparse.ArgumentParser(description="Script for generating an index template out of a document")
    parser.add_argument("INDEX_NAME", help="Name of index")
    parser.add_argument("--output_file", help="File to write schema to")
    args = parser.parse_args()

    output = generate_template(args.INDEX_NAME)
    if args.output_file:
        with open(args.output_file, "w") as file:
            json.dump(output, file, ensure_ascii=False, indent=4, sort_keys=True)
    else:
        print(json.dumps(output, ensure_ascii=False, indent=4, sort_keys=True))

if __name__ == '__main__':
    sys.exit(main())

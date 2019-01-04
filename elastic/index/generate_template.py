"""
Generates an index template for ElasticSearch from the BuildResults document.
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import sys
from elasticsearch_dsl import Index
from elastic.schema.build_results import BuildResults


def main():
    """
    Generates the index template associated with the structure of the BuildResults
    document, allowing it to be uploaded to an ElasticSearch instance.
    """
    parser = argparse.ArgumentParser(description="Script for generating an index template out of a document")
    parser.add_argument("INDEX_NAME", help="Name of index")
    parser.add_argument("--OUTPUT_FILE", help="File to write schema to")
    args = parser.parse_args()

    document = BuildResults(jobName=None, jobLink=None, buildDateTime=None, buildId=None)
    index = Index(args.INDEX_NAME)
    index.document(document)
    index_template = index.as_template(template_name="template")
    print(
        json.dumps(
            index_template.to_dict(),
            ensure_ascii=False,
            indent=4,
            sort_keys=True))


if __name__ == '__main__':
    sys.exit(main())

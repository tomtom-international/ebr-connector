# ebr-connector

[![Azure DevOps builds](https://img.shields.io/azure-devops/build/tomtomweb/GitHub-TomTom-International/19.svg)](https://dev.azure.com/tomtomweb/GitHub-TomTom-International/_build/latest?definitionId=19&branchName=master)
[![Azure DevOps tests](https://img.shields.io/azure-devops/tests/tomtomweb/GitHub-TomTom-International/19.svg)](https://dev.azure.com/tomtomweb/GitHub-TomTom-International/_build/latest?definitionId=19&branchName=master)
[![Azure DevOps coverage](https://img.shields.io/azure-devops/coverage/tomtomweb/GitHub-TomTom-International/19.svg)](https://dev.azure.com/tomtomweb/GitHub-TomTom-International/_build/latest?definitionId=19&branchName=master)
[![PyPI - Version](https://img.shields.io/pypi/v/ebr-connector.svg)](https://pypi.org/project/ebr-connector/)
[![PyPI - License](https://img.shields.io/pypi/l/ebr-connector.svg)](https://pypi.org/project/ebr-connector/)
[![PyPI - Python Versions](https://img.shields.io/pypi/pyversions/ebr-connector.svg)](https://pypi.org/project/ebr-connector/)
[![PyPI - Format](https://img.shields.io/pypi/format/ebr-connector.svg)](https://pypi.org/project/ebr-connector/)
[![PyPI - Status](https://img.shields.io/pypi/status/ebr-connector.svg)](https://pypi.org/project/ebr-connector/)
[![PyUp - Updates](https://pyup.io/repos/github/tomtom-international/ebr-connector/shield.svg)](https://pyup.io/repos/github/tomtom-international/ebr-connector/)

Simple Python package to define a schema for build and test results to be stored in Elasticsearch

## Terms

* **Build**: A single instance of a CI systems build/test execution. It should map to a single URL/URI/UID on a CI system.
* **Build ID**: The ID associated with a given *build* (eg. *1078929*).
* **Job**: A collection of tasks that describe how a *build* should be run. Running a *job* should result in a *build*. In Jenkins this maps to a job/project,
in Quickbuild this maps to a configuration (eg. *cpp-tests*, *root/prod/main*).
* **Product**: Name of product that a given build is associated with.
* **Test Case**: Individual tests (sometimes aggregrations of closely related tests in C++) with result information
* **Test Set**: An aggregated collection of test cases, i.e. a suite

## Test and Suite Separation

Tests and suites have been separated into two arrays rather than having tests nested with suites in this schema in order to better support Grafana
(which has limitations on accessing nested information in ElasticSearch).

Since the build results are stored in one document it is not possible to filter out for example failing test cases only. It is possible to filter build result
documents with failing tests only but the response received will as well contain the successful test cases.

In order to reduce the amount of received data tests have been therefore separated into passed, failed and skipped arrays.

## Schema conventions

Due to the usage of nested types in the schema the Elasticsearch indexer needs to be informed about this. This is achieved by defining a so called [index
template](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-templates.html).

To avoid modifiying the index template whenever the schema is modified we decided to use
[dynamic templates](https://www.elastic.co/guide/en/elasticsearch/reference/current/dynamic-templates.html) to map the types dynamically
based on the following rules (applied in this order):

* Each field has to be prefixed with `br_`
* Fields that should be not available for full text search (*keyword*) are suffixed with `_key` and will be mapped to type *keyword*.
* Fields that are nested are suffixed with `_nested` and will be mapped to type *nested*.
* Fields that are counters are suffixed with `_count` and will be mapped to type *integer*.
* Fields containing `duration` in their name will be mapped to type *float*.
* Fields of type *string* get a raw field (except they are suffixed with `_key`) that can be used for non-full-text-searches and are limited to 256 characters.


## Credits
This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [tomtom-international/cookiecutter-python](https://github.com/tomtom-international/cookiecutter-python) project template.

ElasticSearch Build Results
===========================

Simple Python package to define a schema for build and test results to be stored in logstash.

Terms
-----

* **Build**: A single instance of a CI systems build/test execution. It should map to a single URL/URI/UID on a CI system.
* **Build ID**: The ID associated with a given *build* (eg. *1078929*).
* **Job**: A collection of tasks that describe how a *build* should be run. Running a *job* should result in a *build*. In Jenkins this maps to a job/project, in Quickbuild this maps to a configuration (eg. *cpp-reflection-tests*, *root/greenfield/prod/main*).
* **Product**: Product that a given build is associated with (eg. *Michi*, *NavKit*)
* **Test Case**:  Individual tests (sometimes aggregrations of closely related tests in C++) with result information
* **Test Set**: An aggregated collection of test cases, i.e. a suite

Test and Suite Separation
-------------------------

Tests and suites have been separated into two arrays rather than having tests nested with suites in this schema in order to better support Grafana
(which has limitations on accessing nested information in ElasticSearch).

Since the build results are stored in one document it is not possible to filter out for example failing test cases only. It is possible to filter build result
documents with failing tests only but the response received will as well contain the successful test cases.

In order to reduce the amount of received data tests have been therefore separated into passed, failed and skipped arrays.

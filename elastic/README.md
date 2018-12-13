Terms
=====

* *Build*: A single instance of a CI systems build/test execution. It should map to a single URL/URI/UID on a CI system.
* *Build ID*: The **unique** ID associated with a given *build*
* *Job*: A collection of tasks that describe how a *build* should be run. Running a *job* should result in a *build*. In jenkins this maps to a
  job/project, in Quickbuild this maps to a configuration.
* *Stage*: A component of a *job*, a subset of tasks
* *Product*: Product that a given build is associated with (e.g. Michi)
* *Test Case*: Individual tests (sometimes aggregrations of closely related tests in C++) with result information
* *Test Set*: An aggregated collection of test cases, i.e. a suite

Other Info
==========

Test and Suite Separation
-------------------------

Tests and suites have been separated into two arrays rather than having tests nested with suites in this schema in order to better support Grafana (which has limitations on accessing nested information in ElasticSearch).

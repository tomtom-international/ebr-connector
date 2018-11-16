ElasticSearch Build Results
===========================

Simple Python package to define a schema for build and test results to be stored in logstash.

Examples
--------

Some example usages are provided in the examples folder.
These are subject to change, and may be removed in the future once actual production samples are available.

### jenkins_store

This provides the callback function to copy test results from a Jenkins job and format it into the appropriate schema, and calls the save function in the BuildResults module.

### XunitResults

This provides the callback function to take an Xunit file (or set of files) and converts them into the schema.
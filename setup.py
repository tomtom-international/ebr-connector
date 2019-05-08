#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from __future__ import with_statement

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

import ebr_connector


with open("README.md") as readme_file:
    readme = readme_file.read()

with open("CHANGELOG.md") as changelog_file:
    changelog = changelog_file.read()

requirements = ["elasticsearch-dsl==6.3.1", "requests>=2.18.4,<3"]

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest", "pytest-cov", "coverage", "docker>=3.7.0,<4"]

setup(
    author=ebr_connector.__author__,
    author_email=ebr_connector.__email__,
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="Simple Python package to define a schema for build and test results to be stored in Elasticsearch.",
    entry_points={
        "console_scripts": [
            "ebr-generate-index-template = ebr_connector.index.generate_template:main",
            "ebr-store-jenkins-results = ebr_connector.hooks.jenkins.store_results:main"
        ],
    },
    install_requires=requirements,
    license="Apache License 2.0",
    long_description=readme + "\n\n" + changelog,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="ebr_connector",
    name=ebr_connector.__project__,
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/tomtom-international/ebr-connector",
    version=ebr_connector.__version__,
    zip_safe=False,
)

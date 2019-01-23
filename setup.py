from __future__ import with_statement

from setuptools import setup, find_packages

import elastic

with open("README.md", "r") as fh:
    readme = fh.read()

setup(
    name="ebr-connector",
    version=elastic.__version__,
    author="Eugene Davis",
    author_email="eugene.davis@tomtom.com",
    description="Library that defines the schema used for pushing test results into Elasticsearch",
    long_description=readme,
    url=("https://***REMOVED***/projects/nav/repos/"
         "ebr-connector/browse"),
    packages=find_packages(),
    python_requires=">3.5",
    install_requires=[
        "elasticsearch-dsl>=6.2.1,<7",
        "requests>=2.18.4,<3",
        "qb_results_exporter==0.0.2",
        "junitparser>=1.2.2,<2"
    ],
    setup_requires=["pytest-runner>=4.2,<5"],
    tests_require=[
        "coverage>=4.5,<5"
        "pytest>=4.1,<5",
        "pytest-cov>=2.6,<3"
    ],
    entry_points="""
[console_scripts]
es-generate-index-template = elastic.index.generate_template:main
es-store-quickbuild-results = elastic.hooks.quickbuild.store_results:main
es-store-jenkins-results = elastic.hooks.jenkins.store_results:main
es-store-xunit-results = elastic.hooks.xunit.store_results:main
""",
    dependency_links=[
        "https://***REMOVED***/artifactory/api/pypi/pypi-virtual/simple/qb-results-exporter"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
    license="Apache 2.0",
    zip_safe=False,
)

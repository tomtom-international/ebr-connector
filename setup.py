from __future__ import with_statement

from setuptools import setup, find_packages

with open("README.rst", "r") as fh:
    readme = fh.read()

setup(
    name="ebr-connector",
    version="0.0.1-dev",
    author="Eugene Davis",
    author_email="eugene.davis@tomtom.com",
    description="Library that defines the schema used for pushing test results into Elasticsearch",
    long_description=readme,
    url=("https://***REMOVED***/projects/BERLINCI/repos/"
         "ebr-connector/browse"),
    package_dir = { "ebr-connector/examples": "examples" },
    packages=[ "elastic" ],
    python_requires=">3.5",
    install_requires=[
        "elasticsearch-dsl>=6.2.1,<7",
        "qb_results_exporter"
    ],
    entry_points="""
[console_scripts]
es-build-results-index-template = elastic.generate_index_template:main
es-store-quickbuild-results = elastic.hooks.storeQuickBuildResults:main
""",
    dependency_links=[
        "http://***REMOVED***/artifactory/api/pypi/pypi-virtual/simple/qb-results-exporter"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
    license="Apache 2.0",
    zip_safe=False,
)

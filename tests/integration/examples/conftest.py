"""Helper functions required to set up the environment for the example integration tests.
"""

import random
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from elasticsearch_dsl.connections import connections
from elasticsearch.helpers import bulk
from elasticsearch.helpers.test import get_test_client
import docker

from ebr_connector.schema.build_results import BuildResults
from ebr_connector.index.generate_template import generate_template
from tests import get_test_data_for_failed_build, get_test_data_for_successful_build


def get_index_name():
    """Return name of index.
    """
    return "test_index"


def get_alias_name():
    """Return name of alias.
    """
    return "test_index_alias"


def get_index_data():
    """Return data to be stored in index.
    """
    job_data_set = [
        {
            "callback": get_test_data_for_failed_build,
            "buildstatus": "FAILURE",
            "buildid": 1234,
            "jobname": "cpp-reflection-tests-BB-baseline"
        },
        {
            "callback": get_test_data_for_successful_build,
            "buildstatus": "SUCCESS",
            "buildid": 3,
            "jobname": "cpp-reflection-tests-BB/PR-1234"
        },
        {
            "callback": get_test_data_for_successful_build,
            "buildstatus": "SUCCESS",
            "buildid": 12345,
            "jobname": "cpp-reflection-tests-BB-baseline"
        }]

    index_data = []
    for job_data in job_data_set:
        date_time = (datetime.utcnow()).isoformat()
        build_results = BuildResults.create(job_name=job_data.get("jobname"),
                                            job_link="http://ci/%s" % job_data.get("jobname"),
                                            build_date_time=str(date_time),
                                            build_id=job_data.get("buildid"),
                                            platform="Linux-x86_64", product="MyProduct")
        mock_status_callback = MagicMock()
        mock_status_callback.return_value = job_data.get("buildstatus")
        build_results.store_tests(job_data.get("callback"))
        build_results.store_status(mock_status_callback)
        index_data.append({"_index": get_index_name(), "_type": "doc", "_id": random.getrandbits(128), "_source": build_results.to_dict()})

    return index_data


@pytest.fixture(scope="session")
def elasticsearch_instance():
    """Creates an elasticsearch docker container
    """
    docker_client = docker.from_env()
    try:
        es_container = docker_client.containers.list(filters={"name": "ebr_elasticsearch"})
        if es_container and len(es_container) == 1:
            es_container[0].stop()
            es_container[0].remove()
    except docker.errors.DockerException:
        pass
    es_container = docker_client.containers.run("docker.elastic.co/elasticsearch/elasticsearch-oss:6.5.1",
                                                detach=True, auto_remove=True, ports={"9200": "9200"}, name="ebr_elasticsearch")
    yield
    # try:
    #     es_container.stop()
    # except docker.errors.DockerException:
    #     pass


# pylint: disable=redefined-outer-name,unused-argument
@pytest.fixture(scope="session")
def client(elasticsearch_instance):
    """Return a connection to the elasticsearch server
    """
    connection = get_test_client(nowait=True)
    connections.add_connection("default", connection)
    return connection


def create_index(connection):
    """Creates an test index based on the BuildResults meta data (eg. mapping)
    """
    connection.indices.create(
        index=get_index_name(),
        body=generate_template(get_alias_name()))


# pylint: disable=redefined-outer-name
@pytest.fixture(scope="session")
def data_client(client):
    """Connects to client and stores some test index data in elasticsearch
    """
    create_index(client)
    bulk(client, get_index_data(), raise_on_error=True, refresh=True)
    yield client
    #client.indices.delete(get_index_name())

#
# bento-box
# E2E Test
#
# Requires environment variables to be specified:
# - BENTOBOX_SIM_DOCKER - tag of the bentobox-sim docker image to run

import os
import pytest
from testcontainers.core.container import DockerContainer
from bento.client import Client
from git import Repo

SIM_PORT = 54243


@pytest.fixture
def sim_docker():
    # setup bentobox-sim container and expose sim port
    sim = DockerContainer(os.environ["BENTOBOX_SIM_DOCKER"])
    sim.with_env("BENTOBOX_SIM_PORT", SIM_PORT)
    sim.with_exposed_ports(SIM_PORT)
    sim.start()
    # do e2e test
    yield sim
    # print container logs
    print("====bentobox-sim logs====")
    print(sim.get_wrapped_container().logs())
    # cleanup by stopping sim container at end of test
    sim.stop()


@pytest.fixture
def client(sim_docker):
    # setup bentobox-sdk client
    print(f"{sim_docker.get_container_host_ip()}:{sim_docker.get_exposed_port(SIM_PORT)}")
    client = Client(
        host=sim_docker.get_container_host_ip(),
        port=sim_docker.get_exposed_port(SIM_PORT),
    )
    return client


def test_e2e_sdk_sim_connect(client):
    # e2e test that we can connect to sim/engine via SDK
    assert client.connect(timeout_sec=30)


def test_e2e_engine_get_version(client):
    # e2e test that we can obtain sim/engine's version via SDK
    repo = Repo(search_parent_directories=True)
    assert client.get_version() == repo.head.object.hexsha

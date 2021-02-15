#
# bento-box
# Common E2E Testing Setup & Fixtures
#


import os
import pytest
from distutils.util import strtobool
from testcontainers.core.container import DockerContainer

from bento.client import Client

# port that the engine listens on
ENGINE_PORT = 54242
# whether to start a docker container to provide the engine component in the e2e test
# if False, an engine instance should be already listening at locahost:ENGINE_PORT
# Requires environment variables to be specified:
# - ENGINE_CONTAINER - tag of the bentobox-sim docker image to run
BOOT_ENGINE_CONTAINER = strtobool(
    os.environ.get("BOOT_ENGINE_CONTAINER", default="True")
)


@pytest.fixture
def engine_address():
    print(BOOT_ENGINE_CONTAINER)
    if BOOT_ENGINE_CONTAINER:
        print("e2e: Using Engine Container to provide Engine for E2E")
        # since this fixture as function scope, a fresh Engine instance
        # would be created for each e2e test
        # setup bentobox-sim container and expose engine port
        engine = DockerContainer(os.environ["ENGINE_CONTAINER"])
        engine.with_env("BENTOBOX_SIM_PORT", str(ENGINE_PORT))
        engine.with_env("BENTOBOX_SIM_HOST", "0.0.0.0")
        engine.with_exposed_ports(ENGINE_PORT)
        engine.start()
        # do e2e test
        yield engine.get_container_host_ip(), engine.get_exposed_port(ENGINE_PORT)
        # print the engine's logs
        print("=" * 40, "[Engine Logs]", "=" * 40)
        print(engine._container.logs().decode())
        print("=" * 40, "[Engine Logs]", "=" * 40)
        # cleanup by stopping sim container at end of test
        # kill the container instead of waiting for cleanup
        engine.stop(force=True)
    else:
        print(f"e2e: Using Engine instance listening on localhost:{ENGINE_PORT}")
        print(f"e2e: Warning: Engine instance not reset for each E2E test")
        # perform e2e test on already started engine instance listening on localhost
        yield "localhost", ENGINE_PORT


@pytest.fixture
def client(engine_address):
    # setup bentobox-sdk client
    engine_host, engine_port = engine_address
    client = Client(host=engine_host, port=engine_port)
    # wait for sim to start accepting connections from the SDK
    client.connect(timeout_sec=30)
    return client

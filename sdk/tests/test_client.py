#
# Bentobox
# SDK
# Engine gRPC Client Tests
#

import grpc
import pytest
from concurrent.futures.thread import ThreadPoolExecutor

from bento.client import Client
from bento.protos.services_pb2 import (
    GetVersionReq,
    GetVersionResp,
)
from bento.protos.services_pb2_grpc import (
    EngineServiceServicer,
    add_EngineServiceServicer_to_server,
)


@pytest.fixture
def mock_engine_port():
    """Mock Engine gRPC server fixture that handles test requests"""
    # define servicer that handles requests
    class TestEngine(EngineServiceServicer):
        def GetVersion(self, request, context):
            return GetVersionResp(commit_hash="HASH12")

    # contruct server from servicer
    server = grpc.server(ThreadPoolExecutor())
    add_EngineServiceServicer_to_server(TestEngine(), server)
    # using 0 as tells grpc to automatically choose a port to listen on.
    port = server.add_insecure_port("localhost:0")
    server.start()

    yield port

    # None - stop the server immdiately
    server.stop(None)


@pytest.fixture
def client(mock_engine_port):
    """Return a client configured to talk to the mock Engine gRPC server """
    return Client("localhost", mock_engine_port)


def test_client_connect(client):
    # test constructed client can connect to server
    assert client.connect()


def test_client_get_version(client):
    # test get version call
    assert client.get_version() == "HASH12"

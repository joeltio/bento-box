#
# Bentobox
# SDK
# Engine gRPC Client Tests
#

import grpc
import pytest
from grpc import StatusCode, RpcError
from concurrent.futures.thread import ThreadPoolExecutor

from bento.client import Client
from bento.protos.sim_pb2 import SimulationDef
from bento.protos.services_pb2 import (
    GetVersionReq,
    GetVersionResp,
    ApplySimulationReq,
    ApplySimulationResp,
    GetSimulationReq,
    GetSimulationResp,
    ListSimulationReq,
    ListSimulationResp,
    DropSimulationReq,
    DropSimulationResp,
)
from bento.protos.services_pb2_grpc import (
    EngineServiceServicer,
    add_EngineServiceServicer_to_server,
)
from tests.utils import assert_proto


@pytest.fixture
def sim_def():
    """Mock SimulationDef for testing"""
    return SimulationDef(name="test_sim")


@pytest.fixture
def mock_engine_port(sim_def):
    """Mock Engine gRPC server fixture that handles test requests"""
    # define servicer that handles requests
    class TestEngine(EngineServiceServicer):
        def GetVersion(self, request, context):
            return GetVersionResp(commit_hash="HASH12")

        def ApplySimulation(self, request, context):
            sim = request.simulation
            return ApplySimulationResp(simulation=sim)

        def GetSimulation(self, request, context):
            # mock not found error
            if request.name != sim_def.name:
                context.set_code(StatusCode.NOT_FOUND)
                context.set_details("No simulation with the given name is found.")
            return GetSimulationResp(simulation=sim_def)

        def ListSimulation(self, request, context):
            return ListSimulationResp(sim_names=[sim_def.name])

        def DropSimulation(self, request, context):
            if request.name != sim_def.name:
                context.set_code(StatusCode.NOT_FOUND)
                context.set_details("No simulation with the given name is found.")
            return DropSimulationResp()

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
    assert client.connect(timeout_sec=5)


def test_client_get_version(client):
    # test get version call
    assert client.get_version() == "HASH12"


def test_client_apply_sim(client):
    sim = SimulationDef(name="test_sim")
    got_sim = client.apply_sim(sim)
    assert_proto(got_sim, sim)


def test_client_get_sim(client, sim_def):
    got_sim_def = client.get_sim(sim_def.name)
    assert got_sim_def == sim_def

    # test not found error handling
    has_error = False
    try:
        client.get_sim("not_found")
    except LookupError:
        has_error = True
    assert has_error


def test_client_list_sim(client, sim_def):
    sim_names = client.list_sims()
    assert sim_names == [sim_def.name]


def test_client_remove_sim(client, sim_def):
    client.remove_sim(sim_def.name)

    # test not found error handling
    has_error = False
    try:
        client.remove_sim("not_found")
    except LookupError:
        has_error = True
    assert has_error

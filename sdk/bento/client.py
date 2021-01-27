#
# Bentobox
# SDK
# Engine gRPC Client
#

import grpc

from typing import List
from grpc import RpcError, StatusCode
from bento.protos.sim_pb2 import SimulationDef
from bento.protos.services_pb2_grpc import EngineServiceStub
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


def raise_native(err: RpcError):
    """Convert the given gRPC error into a native exception and raise it."""
    status = err.code()
    if status == StatusCode.DEADLINE_EXCEEDED:
        raise TimeoutError(err.details())
    elif status == StatusCode.UNIMPLEMENTED:
        raise NotImplementedError(err.details())
    elif status == StatusCode.INVALID_ARGUMENT:
        raise ValueError(err.details())
    elif status == StatusCode.NOT_FOUND:
        raise LookupError(err.details())
    elif status == StatusCode.ALREADY_EXISTS:
        raise FileExistsError(err.details())
    elif status == StatusCode.OUT_OF_RANGE:
        raise IndexError(err.details())
    else:
        raise RuntimeError(err.details())


class Client:
    """Client provides methods to interface and with the Engine's API.

    Client sets up a gRPC channel to talk to the Engine's gRPC API providing a
    facade to the RPC calls exposed by the Engine's API, automatically mapping
    between native and Protobuf objects used by gRPC.
    """

    def __init__(self, host: str, port: int):
        """Construct a new Client that connects to the Engine endpoint.

        Args:
            host: Hostname/IP of the host that runs the Engine to connect.
            port: Port number that can be the Engine listens on.
        """
        # try to connect to the engine's grpc endpoint
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        # setup grpc service stubs
        self.sim_grpc = EngineServiceStub(self.channel)

    def connect(self, timeout_sec: int = 30) -> bool:
        """Attempt to connect the configured gRPC Engine endpoint.
        Args:
            timeout_sec: Max no. of seconds to try connecting to the Engine before timing out.
        Returns:
            True if connection attempt is successful.
        Raises:
            TimeoutError: If connection attempt times out.
        """
        try:
            grpc.channel_ready_future(self.channel).result(timeout_sec)
        except grpc.FutureTimeoutError:
            raise TimeoutError(f"Timed out trying to connect to Bentobox Engine")
        return True

    def get_version(self) -> str:
        """Get version info from the Engine instance

        Returns:
            VCS Commit Hash of commit which the engine was built on.
        """
        try:
            response = self.sim_grpc.GetVersion(GetVersionReq())
        except RpcError as e:
            raise_native(e)
        return response.commit_hash

    def apply_sim(self, simulation: SimulationDef):
        """Apply the given simulation to the Engine.
        Creates the simulation if no simulation with the same name exists,
        otherwise updates the existing simulation with the same name.

        Args:
            simulation: Specification of the simulation to apply to the Engine.
        """
        try:
            self.sim_grpc.ApplySimulation(ApplySimulationReq(simulation=simulation))
        except RpcError as e:
            raise_native(e)

    def get_sim(self, name: str) -> SimulationDef:
        """Get the simulation with the given name

        Args:
            name: Name of the simulation to retrieve.
        Returns:
            Specification of the simulation with the given name.
        Raises:
            NameError: If the no simulation with the given is name exists on the Engine.
        """
        try:
            response = self.sim_grpc.GetSimulation(GetSimulationReq(name=name))
        except RpcError as e:
            raise_native(e)
        return response.simulation

    def list_sims(self) -> List[str]:
        """List the names of the simulations registered in the Engine.

        Returns:
            List of the names of the simulations registered in the Engine.
        """
        try:
            response = self.sim_grpc.ListSimulation(ListSimulationReq())
        except RpcError as e:
            raise_native(e)
        return response.sim_names

    def remove_sim(self, name: str):
        """Remove the simulation with the given name.
        Args:
            name: Name of the simulation to remove.
        Raises:
            NameError: If the no simulation with the given is name exists on the Engine.
        """
        try:
            response = self.sim_grpc.DropSimulation(DropSimulationReq(name=name))
        except RpcError as e:
            raise_native(e)

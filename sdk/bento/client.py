#
# Bentobox
# SDK
# Engine gRPC Client
#

import grpc

from bento.protos.services_pb2_grpc import EngineServiceStub
from bento.protos.services_pb2 import GetVersionReq, GetVersionResp


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

    def connect(self, timeout_sec: int = 2) -> bool:
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
        response = self.sim_grpc.GetVersion(GetVersionReq())
        return response.commit_hash

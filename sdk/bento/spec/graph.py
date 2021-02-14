#
# Bentobox
# SDK - ECS
# Graph
#

import yaml
from typing import Iterable


from bento.utils import to_yaml_proto
from bento.protos.graph_pb2 import Node, Graph as GraphProto


class Graph:
    """Represents computation as a computational graph.
    Graph provides a thin wrapper around the the Graph proto which can be accessed
    via the `.proto` attribute.
    """

    def __init__(
        self, inputs: Iterable[Node.Retrieve] = [], outputs: Iterable[Node.Mutate] = []
    ):
        """Construct a Graph with the given inputs and outputs.

        Args:
            inputs: List of retrieve nodes specifying the inputs/arguments required
                to run the computational graph.
            outputs: List of mutate nodes defining the variable changes after
                running the computational graph.

        Sorts graph inputs and outputs as Graph is input/outputs position invariant
        ie the Graph with the same inputs and outputs, but ordered differently should
        still count as the same graph.
        """
        self.proto = GraphProto(inputs=inputs, outputs=outputs)

    @classmethod
    def from_proto(cls, proto: GraphProto):
        """Create a ComponentDef from a Graph proto."""
        return cls(proto.inputs, proto.outputs)

    @property
    def yaml(self):
        """Convert and return this Graph as YAML"""
        return to_yaml_proto(self.proto)

    def __repr__(self):
        return self.yaml

    def __eq__(self, other):
        return self.proto.SerializeToString() == other.proto.SerializeToString()

    def __hash__(self):
        return hash(self.proto.SerializeToString())

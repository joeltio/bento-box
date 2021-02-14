#
# Bentobox
# SDK - Specification
# Simulation Specification
#


from typing import Iterable, List

from bento.protos import sim_pb2
from bento.spec.ecs import ComponentDef, EntityDef, SystemDef
from bento.spec.graph import Graph


class SimulationDef:
    """Specifies a Simulation by defining its entities, components & systems.

    The `SimulationDef` can be 'rehydrated' in an actual `bento.sim.Simulation` by::

        sim = Simulation.from_def(sim_def)

    SimulationDef provides a thin wrapper around the the SimulationDef proto which
    can be accessed via the `.proto` attribute.
    """

    def __init__(
        self,
        name: str,
        components: Iterable[ComponentDef],
        entities: Iterable[EntityDef],
        systems: Iterable[SystemDef] = [],
        init_graph: Graph = Graph(),
    ):
        """Create a SimulationDef with the given name

        Args:
            name: Name to use for the defined Simulation. The name should be
                unique among registered simulations.
            entities: List of entities in use in the simulation.
            components: List of component types in use in the simulation.
            systems: List of systems to run in this simulation.
            init_graph: The init graph to use to initialize attribute values.
        """
        self.proto = sim_pb2.SimulationDef(
            name=name,
            entities=[e.proto for e in entities],
            components=[c.proto for c in components],
            systems=[s.proto for s in systems],
            init_graph=init_graph.proto,
        )

    @classmethod
    def from_proto(cls, proto: sim_pb2.SimulationDef):
        """Create a SimulationDef from a `bento.proto.sim_pb2.SimulationDef Proto"""
        return cls(
            name=proto.name,
            entities=[EntityDef.from_proto(c) for c in proto.entities],
            components=[ComponentDef.from_proto(c) for c in proto.components],
            systems=[SystemDef.from_proto(s) for s in proto.systems],
            init_graph=Graph.from_proto(proto.init_graph),
        )

    @property
    def name(self) -> str:
        """Get the name of Simulation defined by this SimulationDef"""
        return self.proto.name

    @property
    def components(self) -> List[ComponentDef]:
        """Get the component types in the Simulation defined by this SimulationDef"""
        return [ComponentDef.from_proto(c) for c in self.proto.components]

    @property
    def entities(self) -> List[EntityDef]:
        """Get the entities in the Simulation defined by this SimulationDef"""
        return [EntityDef.from_proto(e) for e in self.proto.entities]

    @property
    def systems(self) -> List[SystemDef]:
        """Get the systems running in the Simulation defined by this SimulationDef"""
        return [SystemDef.from_proto(s) for s in self.proto.systems]

    @systems.setter
    def systems(self, system_defs: List[SystemDef]):
        """Set the systems running in the Simulation defined by this SimulationDef"""
        del self.proto.systems[:]
        self.proto.systems.extend([s.proto for s in system_defs])

    @property
    def init_graph(self) -> Graph:
        """Get the init graph used in the Simulation defined by this SimulationDef"""
        return Graph.from_proto(self.proto.init_graph)

    @init_graph.setter
    def init_graph(self, graph: Graph):
        """Set the init graph used in the Simulation defined by this SimulationDef"""
        self.proto.init_graph.CopyFrom(graph.proto)

    def __repr__(self):
        return self.proto.name

    def __hash__(self):
        return hash(self.proto.name)

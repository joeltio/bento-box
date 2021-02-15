#
# Bentobox
# SDK - Specification
# Simulation Specification
#


from typing import Iterable, List, Optional
from bento.graph.compile import ConvertFn, compile_graph

from bento.protos import sim_pb2
from bento.spec.ecs import ComponentDef, EntityDef, SystemDef
from bento.spec.graph import Graph


class SimulationDef:
    """Provides a Specification for a `bento.sim.Simulation`.

    The `SimulationDef` can be hydrated in an actual `bento.sim.Simulation` by:

        sim = Simulation.from_def(sim_def, client)
    """

    def __init__(
        self,
        name: str,
        components: Iterable[ComponentDef],
        entities: Iterable[EntityDef],
        system_fns: Iterable[ConvertFn] = [],
        init_fn: Optional[ConvertFn] = None,
    ):
        """Create a SimulationDef that specifies a Simulation given name.
        `bento.sim.Simulation`s hydrated from this SimulationDef will have the given attributes.

        Args:
            name: Name to use for the specified Simulation. The name should be
                unique among registered simulations.
            entities: List of entities to use in the specified simulation.
            components: List of component types in use in the specified simulation.
            system_fns: List of `bento.graph.compile.compile_graph()` compilable
                function implemnting the systems to run in the specified simulation.
            init_fn: The `bento.graph.compile.compile_graph()` compilable
                function containing the init code for the specified simulation
                that runs the specified Simulation is registered/applied.
        """
        self.name = name
        self.component_defs = list(components)
        self.entity_defs = list(entities)
        self.system_fns = list(system_fns)
        self.init_fn = init_fn

    def system(self, system_fn: ConvertFn):
        """Register a ECS system with the given system_fn in this SimulationDef
        `bento.sim.Simulation`s hydrated from this SimulationDef will have the given ECS system.
        See `bento.sim.Simulation.system()` for more information.
        """
        self.system_fns.append(system_fn)

    def init(self, init_fn: ConvertFn):
        """Register given init_fn as the init graph for this SimulationDef
        `bento.sim.Simulation`s hydrated from this SimulationDef will have the given
        `init_fn` as its init graph.
        See `bento.sim.Simulation.init()` for more information.
        """
        self.init_fn = init_fn

    def __repr__(self):
        return f"{type(self).__name__}<{self.name}>"

    def __hash__(self):
        return hash(self.name)

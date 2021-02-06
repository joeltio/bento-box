#
# Bentobox
# SDK - Simulation
# Simulation
#

from typing import Iterable, Set, List

from bento.client import Client
from bento.ecs.grpc import Entity, Component
from bento.ecs.spec import EntityDef, ComponentDef, SystemDef
from bento.graph.compile import compile_graph, ConvertFn
from bento.protos.graph_pb2 import Graph
from bento.protos.sim_pb2 import SimulationDef


class Simulation:
    # TODO(mrzzy): Add a more complete usage example into docs.
    """Represents a Simulation in running in the Bentobox Engine.

    Example:
    # define simulation with entities and components
    sim = Simulation(name="sim", entities=[ ... ], components=[ ... ], client=client)

    # implement systems running in the simulation
    @sim.system
    def system_fn():
        # ...

    # start-end the simulation using with block
    with sim:
        # simulation is running now ....
    """

    def __init__(
        self,
        name: str,
        entities: Iterable[EntityDef],
        components: Iterable[ComponentDef],
        client: Client,
    ):
        """Create a new simulation with the given entities and component
        Args:
            name: Name of the simulation. Must be unique for all simulations in the Engine.
            entities: List of entities in use jn the simulation.
            component: List of component types in use in the simulation.
            client: Client to use to communicate with the Engine.
        """
        self.name = name
        self.client = client
        self.started = False
        self.component_defs = list(components)
        self.entity_defs = list(entities)
        self.system_defs = []
        self.init_graph = Graph()

        # register sim on engine
        applied_proto = self.client.apply_sim(self.proto)

        # obtain autogen ids for entities and the engine by recreating from applied proto
        self.entity_defs = [EntityDef.from_proto(e) for e in applied_proto.entities]

        # unpack entity and components from proto
        # unpack Entity protos into grpc backed entities (set(components) -> grpc entity)
        self.entity_map = {
            frozenset(e.components): Entity(
                sim_name=self.name,
                entity_id=e.id,
                components=e.components,
                client=self.client,
            )
            for e in self.entity_defs
        }

    @property
    def proto(self) -> SimulationDef:
        """
        Get a Protobuf representation of this simulation.
        """
        proto = SimulationDef(
            name=self.name,
            entities=[e.proto for e in self.entity_defs],
            components=[c.proto for c in self.component_defs],
            systems=[s.proto for s in self.system_defs],
            init_graph=self.init_graph,
        )
        return proto

    def start(self):
        """Starts this Simulation on the Engine.

        If already started, calling `start()` again does nothing.
        """
        # do nothing if already started
        if self.started:
            return
        # commit all changes made (ie systems added) to engine
        applied_proto = self.client.apply_sim(self.proto)
        # obtain autogen ids for systems from the engine by recreating the applied proto
        self.system_defs = [SystemDef.from_proto(s) for s in applied_proto.systems]
        self.started = True

    def stop(self):
        """Stops and removes this Simulation from the Engine.
        Raises:
            RuntimeError: If stop() is called on a simulation that has not started yet.
        """
        if not self.started:
            raise RuntimeError("Cannot stop a Simulation that has not started yet.")
        # cleanup by remove simulation from engine
        self.client.remove_sim(self.name)
        self.started = False

    def entity(self, components: Iterable[str]) -> Entity:
        """Lookup the gRPC entity with the components with the game attached.

        Provides access to ECS entity on the Bentobox Engine via gRPC.

        Args:
            components: Set of the names of the component attached that
                should be attached to the retrieved component.
        Raises:
            ValueError: if component names given contains duplicates
            RuntimeError: If Simulation has not yet stated.
        Returns:
            The gRPC entity with the given list of components attached.
        """
        if not self.started:
            raise RuntimeError(
                "Cannot obtain a gRPC Entity from a Simulation that has not started yet."
            )
        comp_set = frozenset(components)
        # check for duplicates in given components
        if len(comp_set) != len(components):
            raise ValueError("Given component names should not contain duplicates")
        return self.entity_map[comp_set]

    @property
    def entities(self) -> List[Entity]:
        """Get gRPC entities to this Simulation.
        Returns:
            List of entities belonging to this Simulation
        """
        return list(self.entity_map.values())

    def init(self, init_fn: ConvertFn):
        """Register given init_fn as the init graph for this simulation.

        The init graph allows for the initization of attribute's values,
        running on the simulation first step() call, before any systems run.

        Compiles the `init_fn` into a computational graph and registers the
        result as a init graph for this Simulation.

            Example:
            @sim.system
            def system_fn(g):
                # ... implementation of the system ..

        Args:
            system_fn: Function that contains the implementation of the system.
                Must be compilable by `compile_graph()`.
        """
        self.init_graph = compile_graph(init_fn, self.entity_defs, self.component_defs)

    def system(self, system_fn: ConvertFn):
        """Register ECS system with the given system_fn implementation on this Simulation.

        ECS Systems are run every step of simulation and encapsulate the logic of the simulation.

        Compiles the `system_fn` into a computational graph and registers the
        result as a ECS system to run on this Simulation.

            Example:
            @sim.system
            def system_fn(g):
                # ... implementation of the system ..

        Args:
            system_fn: Function that contains the implementation of the system.
                Must be compilable by `compile_graph()`.
        """
        graph = compile_graph(system_fn, self.entity_defs, self.component_defs)
        self.system_defs.append(SystemDef(graph))

    def step(self):
        """Run this simulation for one step

        Runs this simulation's systems in the order they are registered.
        Blocks until all systems of that simulation have finished running.

        The Simulation must have already started before running the simulation with step()`

        Args:
            RuntimeError: If step() is called on a simulation that has not started yet
                or has already been stopped.
        """
        if not self.started:
            raise RuntimeError(
                "Cannot step a simulation that has not started or already stopped."
            )
        self.client.step_sim(self.name)

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        # never suppress exceptions inside with statement
        return False

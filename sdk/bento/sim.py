#
# Bentobox
# SDK - Simulation
# Simulation
#

from typing import Iterable, List, Set

from bento.client import Client
from bento.ecs.grpc import Component, Entity
from bento.graph.compile import ConvertFn, compile_graph
from bento.protos import sim_pb2
from bento.spec.ecs import ComponentDef, EntityDef, SystemDef
from bento.spec.graph import Graph
from bento.spec.sim import SimulationDef


class Simulation:
    # TODO(mrzzy): Add a more complete usage example into docs.
    """Represents a `Simulation` in running in the Bentobox Engine.

    Example:
        Building and running a simulation::

            # either: define simulation with entities and components
            sim = Simulation(name="sim", entities=[ ... ], components=[ ... ], client=client)
            # or: load/hydrate a predefined simulation from a SimulationDef
            sim = Simulation.from_def(sim_def)

            # use an init graph to initalize attribute values
            @sim.init
            def init_fn():
                # initialize values with:  entity[Component].attribute = value

            # implement systems running in the simulation
            @sim.system
            def system_fn():
                # ...

            # start-end the simulation using with block
            with sim:
                # run the simulation for one step
                sim.step()
                # ...
    """

    def __init__(
        self,
        name: str,
        components: Iterable[ComponentDef],
        entities: Iterable[EntityDef],
        client: Client,
        systems: Iterable[SystemDef] = [],
        init_graph: Graph = Graph(),
    ):
        """Create a new simulation with the given entities and component
        Args:
            name: Name of the simulation. Must be unique for all simulations in the Engine.
            entities: List of entities in use in the simulation.
            components: List of component types in use in the simulation.
            client: Client to use to communicate with the Engine.
            systems: List of systems to run in this simulation.
            init_graph: The init graph to use to initialize attribute values.
        """
        self.client = client
        self.started = False
        self.sim_def = SimulationDef(name, components, entities, systems, init_graph)

        # register sim on engine
        # obtain autogen ids for entities and the engine by recreating from applied proto
        applied_proto = self.client.apply_sim(self.proto)
        self.sim_def = SimulationDef.from_proto(applied_proto)

        # unpack entity and components from proto
        # unpack Entity protos into grpc backed entities (set(components) -> grpc entity)
        self.entity_map = {
            frozenset(e.components): Entity(
                sim_name=self.name,
                entity_id=e.id,
                components=e.components,
                client=self.client,
            )
            for e in self.sim_def.entities
        }

    @classmethod
    def from_def(cls, sim_def: SimulationDef, client: Client):
        """
        Hydrate/Load a Simulation from a `bento.spec.SimulationDef`.

        Args:
            sim_def: SimulationDef specification to load the Simulation from.
            client: Client to use to communicate with the Engine.
        """
        return cls(
            name=sim_def.name,
            components=sim_def.components,
            entities=sim_def.entities,
            systems=sim_def.systems,
            init_graph=sim_def.init_graph,
            client=client,
        )

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
        comp_set = frozenset([str(c) for c in components])
        # check for duplicates in given components
        if len(comp_set) != len(list(components)):
            raise ValueError("Given component names should not contain duplicates")
        return self.entity_map[comp_set]

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
        self.sim_def.init(init_fn)

    def system(self, system_fn: ConvertFn):
        """Register a ECS system with the given system_fn on this Simulation.

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
        self.sim_def.system(system_fn)

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

    @property
    def proto(self) -> sim_pb2.SimulationDef:
        """
        Get the `bento.proto.sim_pb2.SimulationDef` Protobuf representation of this simulation.
        """
        return self.sim_def.proto

    @property
    def name(self) -> str:
        """
        Get the Name of this Simulation.
        """
        return self.sim_def.name

    @property
    def entities(self) -> List[Entity]:
        """Get gRPC entities to this Simulation.
        Returns:
            List of entities belonging to this Simulation
        """
        return list(self.entity_map.values())

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        # never suppress exceptions inside with statement
        return False

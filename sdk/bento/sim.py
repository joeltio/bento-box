#
# Bentobox
# SDK - Simulation
# Simulation
#

from typing import Iterable, List, Optional, Set

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
        system_fns: Iterable[ConvertFn] = [],
        init_fn: Optional[ConvertFn] = None,
    ):
        """Create a new simulation with the given entities and component
        Args:
            name: Name of the the Simulation. The name should be unique among
                registered simulation in the Engine.
            entities: List of entities to use in the simulation.
            components: List of component types in use in the simulation.
            client: Client to use to communicate with the Engine when registering
                and interacting with the simulation.
            system_fns: List of `bento.graph.compile.compile_graph()` compilable
                function implemnting the systems to run in the simulation.
            init_fn: The `bento.graph.compile.compile_graph()` compilable
                function containing the init code for the simulation
                that runs the specified Simulation is registered/applied.
        """
        self.name = name
        self.client = client
        self.started = False
        self.component_defs = list(components)
        self.entity_defs = list(entities)
        # (system_fn, system id). 0 to signify unset system id.
        self.system_fns = [(fn, 0) for fn in system_fns]

        self.init_fn = init_fn

        # register sim on engine
        # obtain autogen ids for entities and the engine by recreating from applied proto
        applied_proto = self.client.apply_sim(self.build(include_graphs=False))
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

    @classmethod
    def from_def(cls, sim_def: SimulationDef, client: Client):
        """
        Create/Hydrate a Simulation from a `bento.spec.SimulationDef`.

        Args:
            sim_def: SimulationDef specification to load the Simulation from.
            client: Client to use to communicate with the Engine.
        """
        return cls(
            name=sim_def.name,
            components=sim_def.component_defs,
            entities=sim_def.entity_defs,
            system_fns=sim_def.system_fns,
            init_fn=sim_def.init_fn,
            client=client,
        )

    def build(self, include_graphs: bool = True) -> sim_pb2.SimulationDef:
        """
        Build a `bento.eachproto.sim_pb2.SimulationDef` Proto from this Simulation.

        Args:
            include_graphs: Whether to compile & include graphs in the returned Proto.
                This requires that id to be set for each entity as entity ids
                are required for graph compilation to work.
        Returns:
            The `bento.proto.sim_pb2.SimulationDef` Proto equivalent of this Simulation.
        """
        # compile graphs if requested to be included
        system_defs, init_graph = [], Graph()
        if include_graphs:
            compile_fn = lambda fn: compile_graph(
                fn, self.entity_defs, self.component_defs
            )
            # compile systems graphs
            system_defs = [
                SystemDef(
                    graph=compile_fn(fn),
                    system_id=system_id,
                )
                for fn, system_id in self.system_fns
            ]
            # compile init graph
            init_graph = (
                compile_fn(self.init_fn) if self.init_fn is not None else Graph()
            )

        return sim_pb2.SimulationDef(
            name=self.name,
            entities=[e.proto for e in self.entity_defs],
            components=[c.proto for c in self.component_defs],
            systems=[s.proto for s in system_defs],
            init_graph=init_graph.proto,
        )

    def start(self):
        """Starts this Simulation on the Engine.

        If already started, calling `start()` again does nothing.
        """
        # do nothing if already started
        if self.started:
            return
        # commit entire simulation to (ie including systems/init graph added) to engine
        applied_proto = self.client.apply_sim(self.build(include_graphs=True))
        # obtain autogen ids for systems from the engine by recreating the applied proto
        current_sys_fns = [system_fn for system_fn, _ in self.system_fns]
        self.system_fns = [
            # update system ids for systems by position
            (fn, system_def.id)
            for fn, system_def in zip(current_sys_fns, applied_proto.systems)
        ]
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
        self.init_fn = init_fn

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
        # 0 to signify unset system id
        self.system_fns.append((system_fn, 0))

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

    def __repr__(self):
        return f"{type(self).__name__}<{self.name}>"

    def __hash__(self):
        return hash(self.name)

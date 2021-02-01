#
# Bentobox
# SDK - Simulation
# Simulation
#

from typing import Iterable, Set, List
from bento.client import Client
from bento.ecs.grpc import Entity, Component
from bento.ecs.spec import EntityDef, ComponentDef, SystemDef
from bento.protos.sim_pb2 import SimulationDef


class Simulation:
    # TODO(mrzzy): Add a more complete usage example into docs.
    """Represents a Simulation in running in the Bentobox Engine.

    Example:
    with Simulation(name="sim", entities=[ ... ], components=[ ... ], client=client) as sim:
        # ..

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
        self.proto = SimulationDef(
            name=self.name,
            entities=[e.proto for e in entities],
            components=[c.proto for c in components],
        )
        self.started = False

    def start(self):
        """Starts this Simulation on the Engine.

        Register sim's entities and components as platform on which systems can run on.
        If already started, calling `start()` again does nothing.
        """
        # do nothing if already started
        if self.started:
            return

        # obtain autogenerated ids for entities and systems from the engine.
        self.proto = self.client.apply_sim(self.proto)
        # unpack entity and components from proto
        # unpack Entity protos into grpc backed entities (set(components) -> grpc entity)
        self.entity_map = {
            frozenset(e.components): Entity(
                sim_name=self.name,
                entity_id=e.id,
                components=e.components,
                client=self.client,
            )
            for e in self.proto.entities
        }
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
            KeyError: Lookup the gRPfs

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

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        # never suppress exceptions inside with statement
        return False

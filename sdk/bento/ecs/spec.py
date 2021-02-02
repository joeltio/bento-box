#
# Bentobox
# SDK - ECS
# Specifying ECS Definitions
#

from bento.types import Type
from bento.protos import ecs_pb2
from bento.protos.graph_pb2 import Graph
from typing import Dict, Iterable, List


class ComponentDef:
    """Specifies a ECS component by defining its name and schema.
    ComponentDef provides a thin wrapper around the the ComponentDef proto which
    can be accessed via the `.proto` attribute.
    """

    def __init__(self, name: str, schema: Dict[str, Type]):
        """Create a ComponentDef with the given name and schema.

        Args:
            name: Name to use for the defined ECS Component. The name should be
                unique for each schema.
            schema: Schema defining the attributes embeded within the defined ECS component.
        """
        self.proto = ecs_pb2.ComponentDef(name=name, schema=schema)

    @property
    def name(self) -> str:
        """Get the name of Component defined in this ComponentDef """
        return self.proto.name

    @property
    def schema(self) -> Dict[str, Type]:
        """Get the schema of Component defined in this ComponentDef"""
        return self.proto.schema

    def __repr__(self):
        return self.proto.name

    def __hash__(self):
        return hash(self.proto.name)


class EntityDef:
    """Specifies a ECS entity by defining its components.
    EntityDef provides a thin wrapper around the the EntityDef proto which
    can be accessed via the `.proto` attribute.
    """

    def __init__(self, components: Iterable[ComponentDef], entity_id: int = 0):
        """Create a EntityDef with the given components to attach.

        Args:
            components: List of components to attach with to the ECS entity
                defined by this EntityDef.
        """
        self.proto = ecs_pb2.EntityDef(
            components=[c.name for c in components],
            id=entity_id,
        )

    @property
    def id(self) -> int:
        """Get the id of this entity"""
        return self.proto.id

    @property
    def components(self) -> List[str]:
        """Get the names of the components attached to the ECS entity defined in this EntityDef"""
        return self.proto.components

    def __repr__(self):
        # default id to ? if not yet set by engine
        entity_id = str(self.proto.id) if self.proto.id != 0 else "?"
        return f"{type(self)}<{self.proto.id}>"

    def __hash__(self):
        return hash(self.proto.id)


class SystemDef:
    """Specifies a ECS System by defining its computational graph.
    SystemDef provides a thin wrapper around the the SystemDef proto which
    can be accessed via the `.proto` attribute.
    """

    def __init__(self, graph: Graph):
        """Create a SystemDef with the given computational graph.

        Args:
            graph: computational graph defining the implementation of the ECS system
                defined by this SystemDef.
        """
        self.proto = ecs_pb2.SystemDef(graph=graph)

    @property
    def id(self) -> int:
        """Get the id of this system"""
        return self.proto.id

    @property
    def graph(self) -> Graph:
        """Get the computational graph of ECS system defined in this SystemDef"""
        return self.proto.graph

    def __repr__(self):
        # default id to ? if not yet set by engine
        entity_id = str(self.proto.id) if self.proto.id != 0 else "?"
        return f"{type(self)}<{self.proto.id}>"

    def __hash__(self):
        return hash(self.proto.id)

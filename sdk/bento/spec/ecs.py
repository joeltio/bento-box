#
# Bentobox
# SDK - ECS
# Specifying ECS Definitions
#

from typing import Dict, Iterable, List, Union

from bento.protos import ecs_pb2
from bento.spec.graph import Graph
from bento.types import Type


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

    @classmethod
    def from_proto(cls, proto: ecs_pb2.ComponentDef):
        """Create a ComponentDef from a ComponentDef Proto"""
        return cls(name=proto.name, schema=dict(proto.schema))

    @property
    def name(self) -> str:
        """Get the name of Component defined in this ComponentDef """
        return self.proto.name

    @property
    def schema(self) -> Dict[str, Type]:
        """Get the schema of Component defined in this ComponentDef"""
        return dict(self.proto.schema)

    def __repr__(self):
        return self.proto.name

    def __hash__(self):
        return hash(self.proto.name)


class EntityDef:
    """Specifies a ECS entity by defining its components.
    EntityDef provides a thin wrapper around the the EntityDef proto which
    can be accessed via the `.proto` attribute.
    """

    def __init__(
        self, components: Iterable[Union[ComponentDef, str]], entity_id: int = 0
    ):
        """Create a EntityDef with the given components to attach.

        Args:
            components: List of components or names of components to attach with
                to the ECS entity defined by this EntityDef.
            entity_id: id held by the ECS entity
        """
        self.proto = ecs_pb2.EntityDef(
            components=[str(c) for c in components],
            id=entity_id,
        )

    @classmethod
    def from_proto(cls, proto: ecs_pb2.EntityDef):
        """Create a EntityDef from a EntityDef Proto"""
        return cls(components=proto.components, entity_id=proto.id)

    @property
    def id(self) -> int:
        """Get the id of this entity"""
        return self.proto.id

    @id.setter
    def id(self, entity_id: int):
        """Set the id of this entity"""
        self.proto.id = entity_id

    @property
    def components(self) -> List[str]:
        """Get the names of the components attached to the ECS entity defined in this EntityDef"""
        return list(self.proto.components)

    def __repr__(self):
        # default id to ? if not yet set by engine
        entity_id = str(self.proto.id) if self.proto.id != 0 else "?"
        return f"{type(self)}<{self.proto.id}>"

    def __hash__(self):
        return hash(self.proto.id)


class SystemDef:
    """Specifies a ECS system by defining its computational graph.
    SystemDef provides a thin wrapper around the the SystemDef proto which
    can be accessed via the `.proto` attribute.
    """

    def __init__(self, graph: Graph, system_id: int = 0):
        """Create a SystemDef with the given computational graph.

        Args:
            graph: computational graph defining the implementation of the ECS system
                defined by this SystemDef.
            system_id: id held by the ECS system
        """
        self.proto = ecs_pb2.SystemDef(graph=graph.proto, id=system_id)

    @classmethod
    def from_proto(cls, proto: ecs_pb2.SystemDef):
        """Create a SystemDef from a SystemDef Proto"""
        return cls(graph=Graph.from_proto(proto.graph), system_id=proto.id)

    @property
    def id(self) -> int:
        """Get the id of this system"""
        return self.proto.id

    @property
    def graph(self) -> Graph:
        """Get the computational graph of ECS system defined in this SystemDef"""
        return Graph.from_proto(self.proto.graph)

    def __repr__(self):
        # default id to ? if not yet set by engine
        entity_id = str(self.proto.id) if self.proto.id != 0 else "?"
        return f"{type(self)}<{self.proto.id}>"

    def __hash__(self):
        return hash(self.proto.id)

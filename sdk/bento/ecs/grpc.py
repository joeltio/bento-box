#
# Bentobox
# SDK - ECS
# gRPC based ECS
#


from typing import Any, FrozenSet, Set, List

from bento.ecs import base
from bento.types import Type
from bento.client import Client
from bento.value import wrap, unwrap
from bento.protos.references_pb2 import AttributeRef


class Component(base.Component):
    """Shim replicates a ECS component on the bentobox Engine via gRPC.

    Provides access to a ECS component on the Engine via gRPC, transparently
    performing gRPC requests when attributes are set or retrieved.
    """

    def __init__(self, sim_name: str, entity_id: int, name: str, client: Client):
        # use __dict__ assignment to prevent triggering __setattr__()
        self.__dict__["_sim_name"] = sim_name
        self.__dict__["_entity_id"] = entity_id
        self.__dict__["_name"] = name
        self.__dict__["_client"] = client

    def get_attr(self, name: str) -> Any:
        # retrieve attribute from engine
        value = self._client.get_attr(
            sim_name=self._sim_name,
            attr_ref=AttributeRef(
                entity_id=self._entity_id,
                component=self._name,
                attribute=name,
            ),
        )
        return unwrap(value)

    def set_attr(self, name: str, value: Any):
        # set attribute to value on the engine
        self._client.set_attr(
            sim_name=self._sim_name,
            attr_ref=AttributeRef(
                entity_id=self._entity_id,
                component=self._name,
                attribute=name,
            ),
            value=wrap(value),
        )

    @property
    def component_name(self):
        return self._name


class Entity(base.Entity):
    """Shim replicates a ECS entity on the bentobox Engine via gRPC.

    Provides access to a ECS entity on the Engine via gRPC, transparently
    performing gRPC requests when components are accessed.

    The grpc Entity's grpc Components can be accessed via `.components`.
    """

    def __init__(
        self, sim_name: str, components: List[str], entity_id: int, client: Client
    ):
        self.sim_name = sim_name
        self.component_map = {
            name: Component(sim_name, entity_id, name, client) for name in components
        }
        self.entity_id = entity_id
        self.client = client

    def get_component(self, name: str) -> Component:
        # allow users to specify component class as name
        name = str(name)
        try:
            return self.component_map[name]
        except KeyError:
            raise KeyError(
                f"Cannot get component: Component {name} not attached for entity"
            )

    @property
    def id(self):
        return self.entity_id

    @property
    def components(self) -> FrozenSet[Component]:
        return frozenset(self.component_map.values())

from random import randint
from typing import Any, Iterable, Set
from bento.value import wrap
from bento.ecs.base import Component, Entity
from bento.graph.value import wrap_const
from bento.protos.graph_pb2 import Node
from bento.protos.references_pb2 import AttributeRef
from bento.protos.values_pb2 import Value


class GraphComponent(Component):
    """Shim that reprsents ECS Component when plotting computation graph.

    Provides access to component's attributes during graph plotting.
    Records attribute get/sets performed on component graph input/output nodes
    which can be accessed via `.inputs` and `.outputs` respectively.

    Example:
        # Record operations on component
        component = GraphComponent(...)
        component.y = component.x

        # Obtain graph input/output nodes corresponding to the input/output nodes
        graph_ins, graph_outputs =  component.inputs, component.outputs
    """

    def __init__(self, entity_id: int, name: str):
        # use __dict__ assignment to prevent triggering __setattr__()
        self.__dict__["_entity_id"] = entity_id
        self.__dict__["_name"] = name
        self.__dict__["_inputs"] = []
        self.__dict__["_outputs"] = []

    def get_attr(self, name: str) -> Node:
        # Record the attribute retrieve operation as input graph node
        get_op = Node.Retrieve(
            retrieve_attr=AttributeRef(
                entity_id=self._entity_id,
                component=self._name,
                attribute=name,
            )
        )
        self._inputs.append(get_op)

        return Node(retrieve_op=get_op)

    def set_attr(self, name: str, value: Any):
        # wrap if native value as a constant node, leave nodes untouched
        value = value if isinstance(value, Node) else wrap_const(value)
        # Record the attribute set/mutate operation as output graph node
        set_op = Node.Mutate(
            mutate_attr=AttributeRef(
                entity_id=self._entity_id,
                component=self._name,
                attribute=name,
            ),
            to_node=value,
        )
        self._outputs.append(set_op)

    @property
    def inputs(self):
        """Get the graph input nodes recorded by this Graph component"""
        return self._inputs

    @property
    def outputs(self):
        """Get the graph output nodes recorded by this Graph component"""
        return self._outputs

    def __str__(self):
        # return string representation of graph component
        return f"{self.__class__.__name___}<{self._name}, {self._name}>"


class GraphEntity(Entity):
    """Shim that reprsents ECS Entity when plotting computation graph.

    Provides access to Entity's components during graph plotting.
    The GraphEntity's GraphComponents can be accessed via `.components`.
    """

    def __init__(self, components: Set[str]):
        # TODO(zzy): obtain id from actual entity
        self.id = randint(1, int(1e5))
        self.component_map = {
            name: GraphComponent(self.id, name) for name in components
        }

    def get_component(self, name):
        try:
            return self.component_map[name]
        except KeyError:
            raise ValueError(
                f"Cannot get component: Component {name} not found bound for entity"
            )

    @property
    def components(self):
        """Get the GraphComponents attached to this GraphEntity"""
        return self.component_map.values()

    def __str__(self):
        # return string representation of graph entity
        return f"{self.__class__.__name___}<{self.id}>"

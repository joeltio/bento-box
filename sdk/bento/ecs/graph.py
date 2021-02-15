#
# Bentobox
# SDK - Graph
# Graph based ECS
#

from collections import OrderedDict
from copy import deepcopy
from binascii import crc32
from typing import Any, Iterable, List, Union, FrozenSet, Dict
from bento.types import Type
from bento.utils import to_str_attr
from bento.ecs.base import Component, Entity
from bento.spec.ecs import ComponentDef, EntityDef
from bento.graph.value import wrap_const
from bento.protos.graph_pb2 import Node
from bento.protos.references_pb2 import AttributeRef
from bento.protos.values_pb2 import Value


class GraphNode:
    """Shim that wraps a `bento.protos.graph_pb2.Node` proto to provide operations when building a graph.

    Provides operator overloads for Node proto to provide operations during
    computational graph constructions. Records the operations performed on the Node proto.


    The wrapped Node proto can be obtained via `.node`.
    """

    def __init__(self, node: Node):
        self.node = node

    @classmethod
    def from_attr(cls, entity_id: int, component: str, name: str):
        """Create a GraphNode from the specified ECS attribute"""
        return GraphNode.wrap(
            Node.Retrieve(
                retrieve_attr=AttributeRef(
                    entity_id=entity_id,
                    component=component,
                    attribute=name,
                )
            )
        )

    # use string as return type for compatiblity with python 3.6
    # https://stackoverflow.com/a/33533514
    @classmethod
    def wrap(cls, val: Any) -> "GraphNode":
        """Wraps the given value val as a Graph, performing type conversions if necessary.
        Args:
            val: Native Value, Node proto to wrap as GraphNode
        Returns:
            The given value wrapped as GraphNode
        """
        # check if we are already GraphNode, if so no conversions required.
        if isinstance(val, cls):
            return val
        # convert to Constant node if native value
        node = val if isinstance(val, Node) else wrap_const(val)
        return cls(node=node)

    # arithmetic overloads
    def __add__(self, other: Any):
        other = type(self).wrap(other)
        return type(self).wrap(Node(add_op=Node.Add(x=self.node, y=other.node)))

    def __radd__(self, other: Any):
        other = type(self).wrap(other)
        return type(self).wrap(Node(add_op=Node.Add(x=other.node, y=self.node)))

    def __iadd__(self, other: Any):
        return self.__add__(other)

    def __sub__(self, other: Any):
        other = type(self).wrap(other)
        return type(self).wrap(Node(sub_op=Node.Sub(x=self.node, y=other.node)))

    def __rsub__(self, other: Any):
        other = type(self).wrap(other)
        return type(self).wrap(Node(sub_op=Node.Sub(x=other.node, y=self.node)))

    def __isub__(self, other: Any):
        return self.__sub__(other)

    def __mul__(self, other: Any):
        other = type(self).wrap(other)
        return type(self).wrap(Node(mul_op=Node.Mul(x=self.node, y=other.node)))

    def __rmul__(self, other: Any):
        other = type(self).wrap(other)
        return type(self).wrap(Node(mul_op=Node.Mul(x=other.node, y=self.node)))

    def __imul__(self, other: Any):
        other = type(self).wrap(other)
        return self.__mul__(other)

    def __truediv__(self, other: Any):
        other = type(self).wrap(other)
        return type(self).wrap(Node(div_op=Node.Div(x=self.node, y=other.node)))

    def __itruediv__(self, other: Any):
        other = type(self).wrap(other)
        return self.__truediv__(other)

    def __rtruediv__(self, other: Any):
        other = type(self).wrap(other)
        return type(self).wrap(Node(div_op=Node.Div(x=other.node, y=self.node)))

    def __mod__(self, other: Any):
        other = type(self).wrap(other)
        return type(self).wrap(Node(mod_op=Node.Mod(x=self.node, y=other.node)))

    def __rmod__(self, other: Any):
        other = type(self).wrap(other)
        return type(self).wrap(Node(mod_op=Node.Mod(x=other.node, y=self.node)))

    def __neg__(self):
        # -x is equivalent to 0 - x
        return type(self).wrap(Node(sub_op=Node.Sub(x=wrap_const(0), y=self.node)))

    def __pos__(self):
        # +x is equivalent to x
        return type(self).wrap(self.node)

    # boolean overloads
    def __lt__(self, other: Any):
        other = type(self).wrap(other)
        return type(self).wrap(Node(lt_op=Node.Lt(x=self.node, y=other.node)))

    def __gt__(self, other: Any):
        other = type(self).wrap(other)
        return other.__lt__(self)

    def __eq__(self, other: Any):
        other = type(self).wrap(other)
        return type(self).wrap(Node(eq_op=Node.Eq(x=self.node, y=other.node)))

    def __ne__(self, other: Any):
        other = type(self).wrap(other)
        return Node(not_op=Node.Not(x=self.__eq__(other).node))

    def __le__(self, other: Any):
        other = type(self).wrap(other)
        return type(self).wrap(
            Node(
                or_op=Node.Or(
                    x=self.__lt__(other.node).node, y=self.__eq__(other.node).node
                ),
            )
        )

    def __ge__(self, other: Any):
        other = type(self).wrap(other)
        return type(self).wrap(
            Node(
                or_op=Node.Or(
                    x=self.__gt__(other.node).node, y=self.__eq__(other.node).node
                ),
            )
        )

    def __str__(self):
        return f"{type(self).__name__}<{self.node}>"

    def __hash__(self):
        return hash(self.node)


class GraphComponent(Component):
    """Shim that represents an ECS Component when plotting computation graph.

    Provides access to component's attributes during graph plotting.
    Records operations on attributes which inputs and outputs dictionaries.

        Example:
        # Record operations on component
        component = GraphComponent(...)
        component.y = component.x

        # Obtain graph input/output nodes corresponding to the input/output nodes
        graph_ins, graph_outputs = component.inputs, component.outputs
    """

    # TODO(mrzzy): add schema validation
    def __init__(self, entity_id: int, name: str, schema: Dict[str, Type]):
        # use __dict__ assignment to prevent triggering __setattr__()
        self.__dict__["_entity_id"] = entity_id
        self.__dict__["_name"] = name
        self.__dict__["_schema"] = schema
        # _inputs/_outputs are dict with AttributeRef as key and Retrieve/Mutate nodes as value
        self.__dict__["_inputs"] = OrderedDict()
        self.__dict__["_outputs"] = OrderedDict()

    @classmethod
    def from_def(cls, entity_id: int, component_def: ComponentDef):
        """Construct a GraphComponent from a ComponentDef"""
        # check that ComponentDef's id is set and not protobuf default
        if component_def.name == "":
            raise ValueError(
                "Cannot construct GraphComponent from ComponentDef with unset name"
            )
        return cls(
            entity_id=entity_id,
            name=component_def.name,
            schema=component_def.schema,
        )

    def use_input_outputs(
        self,
        inputs: "OrderedDict[str, GraphNode]",
        outputs: "OrderedDict[str, GraphNode]",
    ):
        """Use the given inputs and output dicts to record attribute operations.
        Useful for implementing a shared inputs and outputs between multiple GraphComponents.

        Args:
            inputs:  Dict to record on when attributes are retrieved with get_attr().
            outputs:  Dict to record on when attributes are set with set_attr().
        """
        self.__dict__["_inputs"] = inputs
        self.__dict__["_outputs"] = outputs

    def get_attr(self, name: str) -> GraphNode:
        attr_ref = AttributeRef(
            entity_id=self._entity_id,
            component=self._name,
            attribute=str(name),
        )
        # check if attribute has been defined in earlier set_attr()
        # if so return that definition to preserve the graph already built for that attribute
        if to_str_attr(attr_ref) in self._outputs:
            built_graph = self._outputs[to_str_attr(attr_ref)].node.mutate_op.to_node
            return GraphNode(built_graph)

        # record the attribute retrieve operation as input graph node
        get_op = GraphNode(node=Node(retrieve_op=Node.Retrieve(retrieve_attr=attr_ref)))
        self._inputs[to_str_attr(attr_ref)] = get_op
        return get_op

    def set_attr(self, name: str, value: Any):
        value = GraphNode.wrap(value)
        attr_ref = AttributeRef(
            entity_id=self._entity_id,
            component=self._name,
            attribute=name,
        )
        # ignore attribute self assignments (ie component.attr = component.attr)
        if (
            value.node.WhichOneof("op") == "retrieve_op"
            and value.node.retrieve_op.retrieve_attr.SerializeToString()
            == attr_ref.SerializeToString()
        ):
            return
        # record the attribute set/mutate operation as output graph node
        set_op = GraphNode(
            node=Node(
                mutate_op=Node.Mutate(
                    mutate_attr=attr_ref,
                    to_node=value.node,
                )
            )
        )
        self._outputs[to_str_attr(attr_ref)] = set_op
        # preserve order of execution in _outputs by moving set operation record to end
        self._outputs.move_to_end(to_str_attr(attr_ref))

    @property
    def component_name(self):
        return self._name

    def __deepcopy__(self, memo):
        # override deepcopy as default implementaion unintentionally
        # triggers get_attr()/set_attr().
        copy = type(self)(self._entity_id, self._name, self._schema)
        # don't deepcopy inputs as collected globally for the entire graph.
        copy.__dict__["_inputs"] = self._inputs
        # deepcopy outputs as they should be scoped with deepcopy()
        copy.__dict__["_outputs"] = deepcopy(self._outputs, memo)

        return copy


class GraphEntity(Entity):
    """Shim that represnets an ECS Entity when plotting computation graph.

    Provides access to Entity's components during graph plotting.
    The GraphEntity's GraphComponents can be accessed via `.components`.
    """

    def __init__(self, components: Iterable[GraphComponent], entity_id: int):
        self.entity_id = entity_id
        self.component_map = {c.component_name: c for c in components}

    @classmethod
    def from_def(cls, entity_def: EntityDef, component_defs: Iterable[ComponentDef]):
        """Construct a GraphEntity from a EntityDef"""
        # check that EntityDef's id is set and not protobuf default
        if entity_def.id == 0:
            raise ValueError("Cannot construct GraphEntity from Entity with unset id")
        return cls(
            components=[
                GraphComponent.from_def(entity_id=entity_def.id, component_def=c)
                for c in component_defs
                if c.name in entity_def.components
            ],
            entity_id=entity_def.id,
        )

    def use_input_outputs(
        self,
        inputs: "OrderedDict[str, GraphNode]",
        outputs: "OrderedDict[str, GraphNode]",
    ):
        """Use the given inputs and output dicts to record attribute operations.
        Useful for implementing a shared inputs and outputs between multiple GraphEntities.

        Args:
            inputs: Dict to record on when this Entity's GraphComponent attributes are retrieved.
            outputs: Dict to record on when this Entity's GraphComponent attributes are set.
        """
        # configure conmponents to use given inputs/outputs dicts
        for component in self.component_map.values():
            component.use_input_outputs(inputs, outputs)

    def get_component(self, name: str) -> GraphComponent:
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
        """Get the id held by this GraphEntity"""
        return self.entity_id

    @property
    def components(self) -> FrozenSet[GraphComponent]:
        """Get the GraphComponent attached to this GraphEntity"""
        return frozenset(self.component_map.values())

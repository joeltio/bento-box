#
# Bentobox
# SDK - Graph
# Graph ECS
#

from random import randint
from typing import Any, Iterable, Set, List
from bento.ecs.base import Component, Entity
from bento.graph.value import wrap_const
from bento.protos.graph_pb2 import Node
from bento.protos.references_pb2 import AttributeRef
from bento.protos.values_pb2 import Value


class GraphNode:
    """Shim that wraps a Node proto to provide operations when building a graph.

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

    @classmethod
    def wrap(cls, val: Any):
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
        return GraphNode(node=node)

    # arithmetic overloads
    def __add__(self, other: Any):
        other = GraphNode.wrap(other)
        return GraphNode.wrap(Node(add_op=Node.Add(x=self.node, y=other.node)))

    def __radd__(self, other: Any):
        other = GraphNode.wrap(other)
        return GraphNode.wrap(Node(add_op=Node.Add(x=other.node, y=self.node)))

    def __iadd__(self, other: Any):
        other = GraphNode.wrap(other)
        # add in-place
        self.node = Node(add_op=Node.Add(x=self.node, y=other.node))
        return self

    def __sub__(self, other: Any):
        other = GraphNode.wrap(other)
        return GraphNode.wrap(Node(sub_op=Node.Sub(x=self.node, y=other.node)))

    def __rsub__(self, other: Any):
        other = GraphNode.wrap(other)
        return GraphNode.wrap(Node(sub_op=Node.Sub(x=other.node, y=self.node)))

    def __isub__(self, other: Any):
        other = GraphNode.wrap(other)
        # subtract in-place
        self.node = Node(add_op=Node.Sub(x=self.node, y=other.node))
        return self

    def __mul__(self, other: Any):
        other = GraphNode.wrap(other)
        return GraphNode.wrap(Node(mul_op=Node.Mul(x=self.node, y=other.node)))

    def __rmul__(self, other: Any):
        other = GraphNode.wrap(other)
        return GraphNode.wrap(Node(mul_op=Node.Mul(x=other.node, y=self.node)))

    def __imul__(self, other: Any):
        other = GraphNode.wrap(other)
        # multiply in-place
        self.node = Node(add_op=Node.Mul(x=self.node, y=other.node))
        return self

    def __truediv__(self, other: Any):
        other = GraphNode.wrap(other)
        return GraphNode.wrap(Node(div_op=Node.Div(x=self.node, y=other.node)))

    def __truediv__(self, other: Any):
        other = GraphNode.wrap(other)
        return GraphNode.wrap(Node(div_op=Node.Div(x=other.node, y=self.node)))

    def __itruediv__(self, other: Any):
        other = GraphNode.wrap(other)
        # divide in-place
        self.node = Node(add_op=Node.Div(x=self.node, y=other.node))
        return self

    def __mod__(self, other: Any):
        other = GraphNode.wrap(other)
        return GraphNode.wrap(Node(mod_op=Node.Mod(x=self.node, y=other.node)))

    def __rmod__(self, other: Any):
        other = GraphNode.wrap(other)
        return GraphNode.wrap(Node(mod_op=Node.Mod(x=other.node, y=self.node)))

    def __neg__(self):
        # -x is equivalent to 0 - x
        return GraphNode.wrap(Node(sub_op=Node.Sub(x=wrap_const(0), y=self.node)))

    def __pos__(self):
        # +x is equivalent to x
        return GraphNode.wrap(self.node)

    # boolean overloads
    def __lt__(self, other: Any):
        other = GraphNode.wrap(other)
        return GraphNode.wrap(Node(lt_op=Node.Lt(x=self.node, y=other.node)))

    def __gt__(self, other: Any):
        other = GraphNode.wrap(other)
        return other.__lt__(self)

    def __eq__(self, other: Any):
        other = GraphNode.wrap(other)
        return GraphNode.wrap(Node(eq_op=Node.Eq(x=self.node, y=other.node)))

    def __ne__(self, other: Any):
        other = GraphNode.wrap(other)
        return Node(not_op=Node.Not(x=self.__eq__(other).node))

    def __le__(self, other: Any):
        other = GraphNode.wrap(other)
        return GraphNode.wrap(
            Node(
                or_op=Node.Or(
                    x=self.__lt__(other.node).node, y=self.__eq__(other.node).node
                ),
            )
        )

    def __ge__(self, other: Any):
        other = GraphNode.wrap(other)
        return GraphNode.wrap(
            Node(
                or_op=Node.Or(
                    x=self.__gt__(other.node).node, y=self.__eq__(other.node).node
                ),
            )
        )

    def __str__(self):
        return f"{self.__class__.__name___}<{self.node}>"

    def __hash__(self):
        return hash(self.node)


class GraphComponent(Component):
    """Shim that represents an ECS Component when plotting computation graph.

    Provides access to component's attributes during graph plotting.
    Records operations on attributes which can be accessed via `.inputs` and `.outputs` respectively.

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
        get_op = GraphNode(
            node=Node(
                retrieve_op=Node.Retrieve(
                    retrieve_attr=AttributeRef(
                        entity_id=self._entity_id,
                        component=self._name,
                        attribute=name,
                    )
                )
            )
        )
        self._inputs.append(get_op)
        return get_op

    def set_attr(self, name: str, value: Any):
        value = GraphNode.wrap(value)
        # Record the attribute set/mutate operation as output graph node
        set_op = GraphNode(
            node=Node(
                mutate_op=Node.Mutate(
                    mutate_attr=AttributeRef(
                        entity_id=self._entity_id,
                        component=self._name,
                        attribute=name,
                    ),
                    to_node=value.node,
                )
            )
        )
        self._outputs.append(set_op)

    @property
    def inputs(self) -> List[GraphNode]:
        """Get the graph input nodes recorded by this Graph component"""
        return self._inputs

    @property
    def outputs(self) -> List[GraphNode]:
        """Get the graph output nodes recorded by this Graph component"""
        return self._outputs

    def __str__(self):
        return f"{self.__class__.__name___}<{self._name}, {self._name}>"


class GraphEntity(Entity):
    """Shim that represnets an ECS Entity when plotting computation graph.

    Provides access to Entity's components during graph plotting.
    The GraphEntity's GraphComponents can be accessed via `.components`.
    """

    def __init__(self, components: Iterable[str]):
        # TODO(zzy): obtain id from actual entity
        self.id = randint(1, int(1e5))
        self.component_map = {
            name: GraphComponent(self.id, name) for name in components
        }

    def get_component(self, name: str) -> GraphComponent:
        try:
            return self.component_map[name]
        except KeyError:
            raise ValueError(
                f"Cannot get component: Component {name} not attached for entity"
            )

    @property
    def components(self) -> Set[str]:
        """Get the GraphComponents attached to this GraphEntity"""
        return set(self.component_map.values())

    def __str__(self):
        return f"{self.__class__.__name___}<{self.id}>"

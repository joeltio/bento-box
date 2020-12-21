#
# Bentobox
# SDK - Graph
# Graph Plotter
#

from random import randint
from typing import Any, Iterable, List, Set
from bento.value import wrap
from bento.ecs.base import Component, Entity
from bento.protos.graph_pb2 import Graph, Node
from bento.protos.values_pb2 import Value
from bento.protos.references_pb2 import AttributeRef


class Plotter:
    """Graph Plotter records operations to plot a computation `Graph`.

    The Graph Plotter records operations performed on a computation graph
    which can be obtained from `graph()` as a `Graph` protobuf message.
    """

    def __init__(self):
        self.inputs, self.outputs = [], []
        self.entity_map = {}

    def entity(self, components: Iterable[str]) -> Entity:
        """
        Find and retrieve the ECS entity with the the given component.

        Args:
            components:
                Set of the names of the unique components to retrieve entity by.
        Raises:
            ValueError: if component names given contains duplicates
        Returns:
            The ECS entity with the given list of components.
        """
        comp_set = frozenset(components)
        # check for duplicates in given components
        if len(comp_set) != len(components):
            raise ValueError("Given component names should not contain duplicates")
        # retrieve entity for components, create if not does not yet exist
        if not comp_set in self.entity_map:
            self.entity_map[comp_set] = GraphEntity(self, comp_set)
        return self.entity_map[comp_set]

    def graph(self) -> Graph:
        """Obtains the computation graph plotted by this Plotter.

        Obtains the computation graph plotted by this Plotter based on the
        operations performed recorded by the Plotter.

        Returns:
            The computation graph plotted by this Plotter as a `Graph` protobuf message.
        """
        return Graph(
            inputs=self.inputs,
            outputs=self.outputs,
        )

    # section: shims - ECS shims records access/assignments to ECS
    def const(self, value: Any) -> Node.Const:
        """Creates a Constant Node that evaluates to the given value

        Args:
            value: Constant value to configure the Constant Node to evaluate to.
        Returns:
            Constant Node protobuf message that evaluates to the given constant value.
        """
        return Node(const_op=Node.Const(held_value=wrap(value)))

    def switch(self, condition: Node, true: Node, false: Node) -> Node.Switch:
        """Creates a conditional Switch Node that evaluates based on condition.

        The switch evalutes to `true` Node if the `condition` Node is true,
        `false` Node otherwise.

        Args:
            condition: Node that defines the condition. Should evaluate to true or false.
            true: Switch Node evaluates to this Node if `condition` evaluates to true.
            false: Switch Node evaluates to this Node if `condition` evaluates to false.

        Return:
            Switch Node protobuf message that evaluates based on the condition Node.
        """
        return Node(
            switch_op=Node.Switch(
                condition_node=condition,
                true_node=true,
                false_node=false,
            )
        )

    # arithmetic operations
    def add(self, x: Node, y: Node) -> Node:
        return Node(add_op=Node.Add(x=x, y=y))

    def sub(self, x: Node, y: Node) -> Node:
        return Node(sub_op=Node.Sub(x=x, y=y))

    def mul(self, x: Node, y: Node) -> Node:
        return Node(mul_op=Node.Mul(x=x, y=y))

    def div(self, x: Node, y: Node) -> Node:
        return Node(div_op=Node.Div(x=x, y=y))

    def max(self, x: Node, y: Node) -> Node:
        return Node(max_op=Node.Max(x=x, y=y))

    def min(self, x: Node, y: Node) -> Node:
        return Node(min_op=Node.Min(x=x, y=y))

    def abs(self, x: Node) -> Node:
        return Node(abs_op=Node.Abs(x=x))

    def floor(self, x: Node) -> Node:
        return Node(floor_op=Node.Floor(x=x))

    def pow(self, x: Node, y: Node) -> Node:
        return Node(pow_op=Node.Pow(x=x, y=y))

    def mod(self, x: Node, y: Node) -> Node:
        return Node(mod_op=Node.Mod(x=x, y=y))

    # trignomomic operations
    def sin(self, x: Node) -> Node:
        return Node(sin_op=Node.Sin(x=x))

    def arcsin(self, x: Node) -> Node:
        return Node(arcsin_op=Node.ArcSin(x=x))

    def cos(self, x: Node) -> Node:
        return Node(cos_op=Node.Cos(x=x))

    def arccos(self, x: Node) -> Node:
        return Node(arccos_op=Node.ArcCos(x=x))

    def tan(self, x: Node) -> Node:
        return Node(tan_op=Node.Tan(x=x))

    def arctan(self, x: Node) -> Node:
        return Node(arctan_op=Node.ArcTan(x=x))

    # random number operation
    def random(self, low: Node, high: Node) -> Node:
        """Creates a Random Node that evaluates to a random float between given `low` and `high`

        Args:
            low: Node that evaluates to the lower bound of the random number generated (inclusive).
            high: Node that evaluates to the upper bound of the random number generated (inclusive).

        Returns:
            Random Node protobuf message that evaluates to a random float between given `low` and `high`
        """
        return Node(random_op=Node.Random(low=low, high=high))

    # boolean operations
    # NOTE: and/or/not are  and_/or_/not_ respectively as they conflict with python keywords
    def and_(self, x: Node, y: Node) -> Node:
        return Node(and_op=Node.And(x=x, y=y))

    def or_(self, x: Node, y: Node) -> Node:
        return Node(or_op=Node.Or(x=x, y=y))

    def not_(self, x: Node, y: Node) -> Node:
        return Node(not_op=Node.Not(x=x, y=y))

    def eq(self, x: Node, y: Node) -> Node:
        return Node(eq_op=Node.Eq(x=x, y=y))

    def gt(self, x: Node, y: Node) -> Node:
        return Node(gt_op=Node.Gt(x=x, y=y))

    def lt(self, x: Node, y: Node) -> Node:
        return Node(lt_op=Node.Lt(x=x, y=y))

    def ge(self, x: Node, y: Node) -> Node:
        return Node(ge_op=Node.Ge(x=x, y=y))

    def le(self, x: Node, y: Node) -> Node:
        return Node(le_op=Node.Le(x=x, y=y))


class GraphComponent(Component):
    """Shim that reprsents ECS Component when plotting computation graph.

    Provides access to component's attributes during graph plotting.
    Records attribute get/sets performed on component as graph computation nodes.
    """

    def __init__(self, plotter: Plotter, entity_id: int, name: str):
        # use __dict__ assignment to prevent triggering __setattr__()
        self.__dict__["_entity_id"] = entity_id
        self.__dict__["_name"] = name
        self.__dict__["_plotter"] = plotter

    def get_attr(self, name: str) -> Node:
        # Record the attribute retrieve operation as input graph node
        get_op = Node.Retrieve(
            retrieve_attr=AttributeRef(
                entity_id=self._entity_id,
                component=self._name,
                attribute=name,
            )
        )
        self._plotter.inputs.append(get_op)

        return Node(retrieve_op=get_op)

    def set_attr(self, name: str, value: Any):
        # wrap native value as a constant node
        value = self._plotter.const(value) if not isinstance(value, Node) else value
        # Record the attribute set/mutate operation as output graph node
        set_op = Node.Mutate(
            mutate_attr=AttributeRef(
                entity_id=self._entity_id,
                component=self._name,
                attribute=name,
            ),
            to_node=value,
        )
        self._plotter.outputs.append(set_op)

    def __str__(self):
        # return string representation of graph component
        return f"{self.__class__.__name___}<{self._entity_id}, {self._name}>"


class GraphEntity(Entity):
    """Shim that reprsents ECS Entity when plotting computation graph.

    Provides access to Entity's components during graph plotting.
    """

    def __init__(self, plotter: Plotter, components: Set[str]):
        # TODO(zzy): obtain id from actual entity
        self.id = randint(1, int(1e5))
        self.components = {
            name: GraphComponent(plotter, self.id, name) for name in components
        }

    def get_component(self, name):
        try:
            return self.components[name]
        except KeyError:
            raise ValueError(
                f"Cannot get component: Component {name} not found bound for entity"
            )

    def __str__(self):
        # return string representation of graph entity
        return f"{self.__class__.__name___}<{self.id}>"

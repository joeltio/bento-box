#
# Bentobox
# SDK - Graph
# Graph Plotter
#

from typing import Any, Iterable, List, Set
from bento.value import wrap
from bento.graph.value import wrap_const
from bento.graph.ecs import GraphEntity, GraphComponent
from bento.ecs.base import Component, Entity
from bento.protos.graph_pb2 import Graph, Node


class Plotter:
    """Graph Plotter records operations to plot a computation `Graph`.

    The Graph Plotter records operations performed on a computation graph
    which can be obtained from `graph()` as a `Graph` protobuf message.
    """

    def __init__(self):
        self.entity_map = {}

    def entity(self, components: Iterable[str]) -> Entity:
        """
        Get the entity with the given components attached.

        Provides access to component state when building the computation graph.

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
            self.entity_map[comp_set] = GraphEntity(comp_set)
        return self.entity_map[comp_set]

    def graph(self) -> Graph:
        """Obtains the computation graph plotted by this Plotter.

        Obtains the computation graph plotted by this Plotter based on the
        operations recorded by the Plotter.

        Returns:
            The computation graph plotted by this Plotter as a `Graph` protobuf message.
        """
        # Extract graph inputs and outputs from GraphEntities and GraphComponents
        inputs, outputs = [], []
        for entity in self.entity_map.values():
            for component in entity.components:
                inputs.extend(component.inputs)
                outputs.extend(component.outputs)

        return Graph(inputs=inputs, outputs=outputs)

    # section: shims - ECS shims records access/assignments to ECS
    def const(self, value: Any) -> Node.Const:
        """Creates a Constant Node that evaluates to the given value

        Args:
            value: Constant value to configure the Constant Node to evaluate to.
        Returns:
            Constant Node protobuf message that evaluates to the given constant value.
        """
        return wrap_const(value)

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

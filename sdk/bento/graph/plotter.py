#
# Bentobox
# SDK - Graph
# Graph Plotter
#

from typing import Any, List
from bento.protos.graph_pb2 import Graph, Node
from bento.protos.values_pb2 import Value
from bento.value import wrap


class EntityShim(object):

    """Docstring for  EntityShim. """

    def __init__(self):
        """TODO: to be defined. """


class Plotter:
    """Graph Plotter records operations to plot a computation `Graph`.

    The Graph Plotter records operations performed on a computation graph
    which can be obtained from `graph()` as a `Graph` protobuf message.
    """

    def __init__(self):
        self.inputs, self.outputs = [], []

    def entity(self, components):
        # TODO: to be defined
        return EntityShim()

    def graph(self) -> Graph:
        """Obtains the computation graph plotted by this Plotter.

        Obtains the computation graph plotted by this Plotter based on the
        operations performed recorded by the Plotter.

        Returns:
            The computation graph plotted by this Plotter as a `Graph` protobuf message.
        """
        # TODO: to be defined
        return Graph()

    # section: shims - ECS shims records access/assignments to ECS
    def const(self, value: Any) -> Node.Const:
        """Creates a Constant Node that evaluates to the given value

        Args:
            value: Constant value to configure the Constant Node to evaluate to.
        Returns:
            Constant Node protobuf message that evaluates to the given constant value.
        """
        return Node.Const(held_value=wrap(value))

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
        return Node.Switch(
            condition_node=condition,
            true_node=true,
            false_node=false,
        )

    # arithmetic operations
    def add(self, x: Node, y: Node) -> Node:
        return Node.Add(x, y)

    def sub(self, x: Node, y: Node) -> Node:
        return Node.Sub(x, y)

    def mul(self, x: Node, y: Node) -> Node:
        return Node.Mul(x, y)

    def div(self, x: Node, y: Node) -> Node:
        return Node.Div(x, y)

    def max(self, x: Node, y: Node) -> Node:
        return Node.Max(x, y)

    def min(self, x: Node, y: Node) -> Node:
        return Node.Min(x, y)

    def abs(self, x: Node) -> Node:
        return Node.Abs(x)

    def floor(self, x: Node) -> Node:
        return Node.Floor(x)

    def pow(self, x: Node, y: Node) -> Node:
        return Node.Pow(x, y)

    def mod(self, x: Node, y: Node) -> Node:
        return Node.Mod(x, y)

    # trignomomic operations
    def sin(self, x: Node) -> Node:
        return Node.Sin(x)

    def arcsin(self, x: Node) -> Node:
        return Node.ArcSin(x)

    def cos(self, x: Node) -> Node:
        return Node.Cos(x)

    def arccos(self, x: Node) -> Node:
        return Node.ArcCos(x)

    def tan(self, x: Node) -> Node:
        return Node.Tan(x)

    def arctan(self, x: Node) -> Node:
        return Node.ArcTan(x)

    # random number operation
    def random(self, low: Node, high: Node) -> Node:
        """Creates a Random Node that evaluates to a random float between given `low` and `high`

        Args:
            low: Node that evaluates to the lower bound of the random number generated (inclusive).
            high: Node that evaluates to the upper bound of the random number generated (inclusive).

        Returns:
            Random Node protobuf message that evaluates to a random float between given `low` and `high`
        """
        return Node.Random(low, high)

    # boolean operations
    # NOTE: and/or/not are  and_/or_/not_ respectively as they conflict with python keywords
    def and_(self, x: Node, y: Node) -> Node:
        return Node.And(x, y)

    def or_(self, x: Node, y: Node) -> Node:
        return Node.Or(x, y)

    def not_(self, x: Node, y: Node) -> Node:
        return Node.Not(x, y)

    def eq(self, x: Node, y: Node) -> Node:
        return Node.Eq(x, y)

    def gt(self, x: Node, y: Node) -> Node:
        return Node.Gt(x, y)

    def lt(self, x: Node, y: Node) -> Node:
        return Node.Lt(x, y)

    def ge(self, x: Node, y: Node) -> Node:
        return Node.Ge(x, y)

    def le(self, x: Node, y: Node) -> Node:
        return Node.Le(x, y)

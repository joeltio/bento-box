#
# Bentobox
# SDK - Graph
# Graph Plotter
#

from typing import Any, Iterable

from bento.graph.value import wrap_const
from bento.protos.graph_pb2 import Graph, Node
from bento.ecs.spec import EntityDef, ComponentDef
from bento.ecs.graph import GraphEntity, GraphComponent, GraphNode


class Plotter:
    """Graph Plotter records operations to plot a computation `Graph`.

    The Graph Plotter records operations performed on a computation graph
    which can be obtained from `graph()` as a `Graph` protobuf message.
    """

    def __init__(self, entities: Iterable[GraphEntity] = []):
        # map components set to entity id
        self.entity_map = {
            frozenset([c.component_name for c in entity.components]): entity
            for entity in entities
        }

    def entity(self, components: Iterable[str]) -> GraphEntity:
        """
        Get the entity with the components with the game attached.

        Provides access to component state when building the computation graph.

        Args:
            components: Set of the names of the component that should be attached
                to the retrieved component.
        Raises:
            ValueError: If component names given contains duplicates
            KeyError: If no Entity found with the given set of components attached.
        Returns:
            The ECS entity with the given list of components.
        """
        comp_set = frozenset(components)
        # check for duplicates in given components
        if len(comp_set) != len(components):
            raise ValueError("Given component names should not contain duplicates")
        # retrieve entity for components, create if not does not yet exist
        if comp_set not in self.entity_map:
            raise KeyError("No entity found with the given components attached")
        return self.entity_map[comp_set]

    def graph(self) -> Graph:
        """Obtains the computation graph plotted by this Plotter.

        Obtains the computation graph plotted by this Plotter based on the
        operations recorded by the Plotter.

        Returns:
            The computation graph plotted by this Plotter as a `Graph` protobuf message.
        """
        # Extract graph inputs and outputs nodes from GraphComponent's GraphNodes
        inputs, outputs = [], []
        for entity in self.entity_map.values():
            for component in entity.components:
                inputs.extend([i.node.retrieve_op for i in component.inputs])
                outputs.extend([o.node.mutate_op for o in component.outputs])

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

    def switch(self, condition: Any, true: Any, false: Any) -> GraphNode:
        """Creates a conditional Switch Node that evaluates based on condition.

        The switch evalutes to `true` if the `condition` is true, `false` otherwise.

        Args:
            condition: Defines the condition. Should evaluate to true or false.
            true: Switch Node evaluates to this expression if `condition` evaluates to true.
            false: Switch Node evaluates to this expression if `condition` evaluates to false.
        Return:
            Switch Node Graph Node that evaluates based on the condition Node.
        """
        condition, true, false = (
            GraphNode.wrap(condition),
            GraphNode.wrap(true),
            GraphNode.wrap(false),
        )
        return GraphNode.wrap(
            Node(
                switch_op=Node.Switch(
                    condition_node=condition.node,
                    true_node=true.node,
                    false_node=false.node,
                )
            )
        )

    # arithmetic operations
    def max(self, x: Any, y: Any) -> GraphNode:
        x, y = GraphNode.wrap(x), GraphNode.wrap(y)
        return GraphNode(node=Node(max_op=Node.Max(x=x.node, y=y.node)))

    def min(self, x: Any, y: Any) -> GraphNode:
        return GraphNode(node=Node(min_op=Node.Min(x=x.node, y=y.node)))

    def abs(self, x: Any) -> GraphNode:
        x, y = GraphNode.wrap(x), GraphNode.wrap(y)
        return GraphNode(node=Node(abs_op=Node.Abs(x=x)))

    def floor(self, x: Any) -> GraphNode:
        x = GraphNode.wrap(x)
        return GraphNode(node=Node(floor_op=Node.Floor(x=x.node)))

    def ceil(self, x: Any) -> GraphNode:
        x = GraphNode.wrap(x)
        return GraphNode(node=Node(ceil_op=Node.Ceil(x=x.node)))

    def pow(self, x: Any, y: Any) -> GraphNode:
        x, y = GraphNode.wrap(x), GraphNode.wrap(y)
        return GraphNode(node=Node(pow_op=Node.Pow(x=x.node, y=y.node)))

    def mod(self, x: Any, y: Any) -> GraphNode:
        x, y = GraphNode.wrap(x), GraphNode.wrap(y)
        return GraphNode(node=Node(mod_op=Node.Mod(x=x.node, y=y.node)))

    # trigonometric operations
    def sin(self, x: Any) -> GraphNode:
        x = GraphNode.wrap(x)
        return GraphNode(node=Node(sin_op=Node.Sin(x=x.node)))

    def arcsin(self, x: Any) -> GraphNode:
        x = GraphNode.wrap(x)
        return GraphNode(node=Node(arcsin_op=Node.ArcSin(x=x.node)))

    def cos(self, x: Any) -> GraphNode:
        x = GraphNode.wrap(x)
        return GraphNode(node=Node(cos_op=Node.Cos(x=x.node)))

    def arccos(self, x: Any) -> GraphNode:
        x = GraphNode.wrap(x)
        return GraphNode(node=Node(arccos_op=Node.ArcCos(x=x.node)))

    def tan(self, x: Any) -> GraphNode:
        x = GraphNode.wrap(x)
        return GraphNode(node=Node(tan_op=Node.Tan(x=x.node)))

    def arctan(self, x: Any) -> GraphNode:
        x = GraphNode.wrap(x)
        return GraphNode(node=Node(arctan_op=Node.ArcTan(x=x.node)))

    # random number operation
    def random(self, low: Any, high: Any) -> GraphNode:
        """Creates a Random Node that evaluates to a random float in range [`low`,`high`]

        Args:
            low: Expression that evaluates to the lower bound of the random number generated (inclusive).
            high: Expression that evaluates to the upper bound of the random number generated (inclusive).

        Returns:
            Random Graph Node that evaluates to a random float in range [`low`,`high`]
        """
        low, high = GraphNode.wrap(low), GraphNode.wrap(high)
        return GraphNode(node=Node(random_op=Node.Random(low=low.node, high=high.node)))

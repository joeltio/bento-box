#
# Bentobox
# SDK - Graph
# Transforms
#

import gast
from typing import Callable
from gast import AST, Constant, Assign, List, Tuple
from bento.graph.plotter import Plotter
from bento.graph.ast import parse_ast, call_func_ast


class FuncASTTransform(gast.NodeTransformer):
    """Defines a AST transformation with a given transform function"""

    def __init__(self, transform_fn: Callable[[AST], AST]):
        super().__init__()
        self.transform_fn = transform_fn

    def visit(self, node: AST) -> AST:
        # recursively visit child nodes
        new_node = super().visit(node)
        # on visit: transform node and fix code locations
        new_node = gast.copy_location(new_node=self.transform_fn(node), old_node=node)
        new_node = gast.fix_missing_locations(new_node)

        return new_node


def transform_const(ast: AST) -> AST:
    """Transforms constant literals in AST to plot Constant Nodes on graph

    Transforms constant literals such as '2' into a call to the Graph Plotter
    to plot a Constant Node `g.constant(2)` on the computation graph.

    Args:
        ast: AST to transform constant literals into constant nodes
    Returns:
        The given ast with the constant nodes transforms
    """

    # define constant AST transform
    def do_transform(literal: AST) -> AST:
        # only perform transform on constant literals
        if not literal.is_constant:
            return literal
        # subsitute constant literals with a constant node plotted graph
        plot_const_ast = parse_ast(Plotter.const).body[0]
        call_plot_ast = call_func_ast(
            attr_parent=ast.convert_fn.plotter_name,
            fn=plot_const_ast,
            args={"value": literal},
        )
        # make call qualified by refering plotter
        return call_plot_ast

    const_transform = FuncASTTransform(do_transform)

    # apply const transform to AST
    ast = const_transform.visit(ast)

    return ast


def transform_build_graph(ast: AST) -> AST:
    """Transforms convert function to build graph function

    Removes the convert function's annotations and changes the name to `build_graph`

    Args:
        ast: AST with the convert function to transform
    Returns:
        The given ast with the convert function transformed to build graph function
    """
    fn_ast = ast.convert_fn
    fn_ast.decorator_list, fn_ast.name = [], "build_graph"

    return ast

#
# Bentobox
# SDK - Graph
# Transforms
#

import gast
from typing import Callable
from gast import AST, Constant, Assign, List, Tuple, IfExp
from bento.graph.plotter import Plotter
from bento.graph.ast import parse_ast, call_func_ast


class FuncASTTransform(gast.NodeTransformer):
    """Defines a AST transformation with a given transform_fn transform function.

    Walks the AST with the given transform_fn, allowing it to modify AST nodes.

    Args:
        transform_fn: transform function that takes in AST and returns the modified AST.
    """

    def __init__(self, transform_fn: Callable[[AST], AST]):
        super().__init__()
        self.transform_fn = transform_fn

    def visit(self, node: AST) -> AST:
        # recursively visit child nodes
        super().visit(node)
        # on visit: transform node and fix code locations
        new_node = gast.copy_location(new_node=self.transform_fn(node), old_node=node)
        new_node = gast.fix_missing_locations(new_node)

        return new_node


def transform_build_graph(ast: AST) -> AST:
    """Transforms convert function to build graph function

    Requires the `analyze_convert_fn()` to analyze the AST first.
    Removes the convert function's annotations and changes the name to `build_graph`

    Args:
        ast: AST with the convert function to transform
    Returns:
        The given ast with the convert function transformed to build graph function
    """
    fn_ast = ast.convert_fn
    fn_ast.decorator_list, fn_ast.name = [], "build_graph"

    return ast


def transform_ternary(ast: AST) -> AST:
    """Transforms ternary conditional to plot Switch Nodes on computational graph.

    Requires the `analyze_convert_fn()` to analyze the AST first.
    Transforms ternary conditionals in the form `a if b else c` into a call to the
    Graph  Plotter to plot a Switch Node `g.switch(b, a, c)` on the computation graph.

    Args:
        ast: AST to transform ternary into a plotting of a Switch Node.
    Returns:
        The given ast with ternary conditional transformed into a plotting of a Switch Node.
    """

    def do_transform(ternary_ast: AST) -> AST:
        # filter out non-ternary expressions
        if not isinstance(ternary_ast, IfExp):
            return ternary_ast
        # obtain AST of calling the plotter to plotting a switch node
        plot_switch_fn = parse_ast(Plotter.switch).body[0]
        return call_func_ast(
            fn=plot_switch_fn,
            args={
                "condition": ternary_ast.test,
                "true": ternary_ast.body,
                "false": ternary_ast.orelse,
            },
            attr_parent=ast.convert_fn.plotter_name,
        )

    ternary_transform = FuncASTTransform(do_transform)

    # apply ternary transform to AST
    ast = ternary_transform.visit(ast)

    return ast

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
        super().visit(node)
        # on visit: transform node and fix code locations
        new_node = gast.copy_location(new_node=self.transform_fn(node), old_node=node)
        new_node = gast.fix_missing_locations(new_node)

        return new_node


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

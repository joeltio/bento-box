#
# Bentobox
# SDK - Graph
# Transforms
#

import gast
from typing import Callable
from gast import AST, Constant, Assign, List, Tuple
from bento.graph.plotter import Plotter
from bento.graph.ast import parse_ast, call_func_ast, FuncASTTransform


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

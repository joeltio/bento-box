#
# Bentobox
# SDK - Graph
# Analyzers
#

import gast

from collections import deque
from math import inf
from typing import List
from gast import (
    AST,
    Constant,
    List,
    Tuple,
    Pass,
    FunctionDef,
    Expr,
    Load,
    Del,
    Store,
    Assign,
    AugAssign,
    AnnAssign,
    Name,
    Attribute,
)


def analyze_func(ast: AST) -> AST:
    """Annotate `FunctionDef` nodes in the given AST with additional infomation

    Walks through the `FunctionDef` nodes in given AST and annotates
    each node with the following info:
    - `n_args`: the function's arguments count.
    - `docstr`: the function's docstring if present, otherwise None
    - `is_empty`: whether the function is empty.
    - `is_generator`: whether the function produces a generator via `yield`.

    Args:
        ast:
            AST to scan for and annotate `FunctionDef` in.

    Returns:
        The given AST with the `FunctionDef` annotated with additional infomation.
    """
    # walk through AST to find FunctionDef nodes
    fn_asts = [n for n in gast.walk(ast) if isinstance(n, FunctionDef)]
    for fn_ast in fn_asts:
        fn_ast.n_args = len(fn_ast.args.args)
        fn_ast.docstr = gast.get_docstring(fn_ast)
        # detect empty if contains pass and/or just a docstrings
        fn_ast.is_empty = True
        for node in fn_ast.body:
            if isinstance(node, Pass):
                continue
            if (
                isinstance(node, Expr)
                and isinstance(node.value, Constant)
                and isinstance(node.value.value, str)
            ):
                continue
            fn_ast.is_empty = False
        # detect as generator if contains yield statement
        fn_ast.is_generator = any(
            isinstance(node, gast.Yield) for node in gast.walk(fn_ast)
        )

    return ast


def analyze_convert_fn(ast: AST) -> AST:
    """Finds and Annotates the target convert function AST

    Requires `analyze_func()` to analyze to the AST first.
    Assumes the target convert function is the first child node of AST.
    Annotates the top level node with the target convert `FunctionDef` node as
    `convert_fn`, otherwise set to `None`.
    Additionally annotates `convert_fn` if present with:
    - `plotter_name` - name of the plotter instance passed to `convert_fn`

    Args:
        ast:
            AST to scan and annotate the target convert function.

    Returns:
        The given AST with the target convert function annotated as `convert_fn`
    """
    # TODO(mrzzy): Allow convert_fn with default args ie def convert_fn(g, a=2, b=3):
    # walk through the AST to find the top level node with min nesting
    candidate_fns = [
        n for n in gast.iter_child_nodes(ast) if isinstance(n, FunctionDef)
    ]
    ast.convert_fn = candidate_fns[0] if len(candidate_fns) == 1 else None

    # extract name of plotter argument if present
    if ast.convert_fn is not None and ast.convert_fn.n_args == 1:
        ast.convert_fn.plotter_name = ast.convert_fn.args.args[0].id

    return ast

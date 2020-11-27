#
# Bentobox
# SDK - Graph
# Analyzers
#

import gast

from math import inf
from typing import List
from gast import AST, FunctionDef, ClassDef, Lambda, Pass, Expr, Constant


def analyze_func(ast: AST) -> AST:
    """Annotate `FunctionDef` nodes in the given AST with additional infomation

    Walks through the `FunctionDef` nodes in given AST and insects annotates
    each node with the following info:
    - `n_args`: the function's arguments count.
    - `has_docstr`: the function's contains a docstring as its first expression
    - `is_empty`: whether the function is empty.
    - `is_generator`: whether the function produces a generator via `yield`.
    - `is_convert_fn`: whether the conversion.

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
        fn_ast.has_docstr = False if gast.get_docstring(fn_ast) is None else True
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
            [isinstance(node, gast.Yield) for node in gast.walk(fn_ast)]
        )

    return ast


def analyze_convert_fn(ast: AST) -> AST:
    """Finds and Annotates the target convert function

    Assumes the target convert function is the first child node of AST.
    Annotates the top level node with the target convert `FunctionDef` node as
    `convert_fn`, otherwise set to `None`.

    Args:
        ast:
            AST to scan and annotate the target convert function.

    Returns:
        The given AST with with the target convert function annotated as `convert_fn`
    """
    # walk through the AST to find the top level node with min nesting
    canidates_fn = [n for n in gast.iter_child_nodes(ast) if isinstance(n, FunctionDef)]
    ast.convert_fn = canidates_fn[0] if len(canidates_fn) == 1 else None
    return ast

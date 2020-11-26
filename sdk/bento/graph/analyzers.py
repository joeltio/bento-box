#
# Bentobox
# SDK - Graph
# Analyzers
#

import gast

from math import inf
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


def analyze_nesting(ast: AST) -> AST:
    """Annotate each AST node with its level of nesting in the given AST tree.

    Walks through each node in the given AST tree and annotates its level of nesting
    as a number `n_nesting`. Each `ClassDef`, `FunctionDef` and `Lambda` node creates
    a new layer of nesting.

    Args:
        ast: AST to scan and annotate nesting of each node in.

    Returns:
        The given AST with each node annotated  with its level of nesting.
    """

    def label_nest_recusive(node: AST, n_nesting: int = 0):
        node.n_nesting = n_nesting
        # increase nesting count if we encounter class or function nodes
        if any([isinstance(node, c) for c in [ClassDef, FunctionDef, Lambda]]):
            n_nesting += 1
        # recusively label the nesting of child nodes
        for child_node in gast.iter_child_nodes(node):
            label_nest_recusive(child_node, n_nesting)
        return node

    return label_nest_recusive(ast)


def analyze_convert_fn(ast: AST) -> AST:
    """Finds and Annotates the target convert function

    Depends on `analyze_nesting` analyzer.
    Assumes the target convert function to be converted to the computation graph
    is the first child node of AST.
    nodes with `is_convert_fn` to mark if it is the target function.
    Also annotates the top level node with `missing_convert_fn` depending on whether
    a target function is found at all.

    Args:
        ast:
            AST to scan and annotate the target convert function.

    Returns:
        The given AST with with the target convert function annoated.
    """
    # walk through the AST to find the top level node with min nesting
    canidates_fn = [n for n in gast.iter_child_nodes(ast) if isinstance(n, FunctionDef)]
    convert_fn = canidates_fn[0] if len(canidates_fn) == 1 else None

    # mark ast as missing convert fn if no top node found
    if convert_fn is None:
        ast.missing_convert_fn = True
        return ast
    # mark top node as target convert fn
    convert_fn.is_convert_fn = True
    ast.missing_convert_fn = False
    return ast

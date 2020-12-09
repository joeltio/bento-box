#
# Bentobox
# SDK - Graph
# Analyzers
#

import gast

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
)


def analyze_func(ast: AST) -> AST:
    """Annotate `FunctionDef` nodes in the given AST with additional infomation

    Walks through the `FunctionDef` nodes in given AST and annotates
    each node with the following info:
    - `n_args`: the function's arguments count.
    - `docstr`: the function's docstring if present, otherwise None
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
            [isinstance(node, gast.Yield) for node in gast.walk(fn_ast)]
        )

    return ast


def analyze_convert_fn(ast: AST) -> AST:
    """Finds and Annotates the target convert function AST

    Assumes the target convert function is the first child node of AST.
    Annotates the top level node with the target convert `FunctionDef` node as
    `convert_fn`, otherwise set to `None`.

    Args:
        ast:
            AST to scan and annotate the target convert function.

    Returns:
        The given AST with the target convert function annotated as `convert_fn`
    """
    # walk through the AST to find the top level node with min nesting
    canidates_fn = [n for n in gast.iter_child_nodes(ast) if isinstance(n, FunctionDef)]
    ast.convert_fn = canidates_fn[0] if len(canidates_fn) == 1 else None
    return ast


def analyze_assign(ast: AST) -> AST:
    """Finds and Annotes assignments in the given AST with additional infomation

    Walks through the assignment nodes in given AST and annotates
    each node with the following info:
    - `n_targets`: no. of targets variables this assignments assign to.
    - `is_unpack`: Whether this assignment unpacks values from a List or Tuple.
    - `is_multi`: Whether this assignment assigns the same value to multiple variables.
    - `n_values`: no. of values this assignment attempts to assign.
    Annotates assignment's targets and values with reference to assignment `assign`.

    Args:
        ast:
            AST to scan and label constant literals.
    Returns:
        The given AST with the assignments annotated.
    """
    assign_types = (
        Assign,
        AnnAssign,
        AugAssign,
    )
    assign_asts = [n for n in gast.walk(ast) if isinstance(n, assign_types)]

    for assign_ast in assign_asts:
        iterable_types = (List, Tuple)
        assign_ast.is_unpack, assign_ast.is_multi = False, False
        if isinstance(assign_ast, Assign):
            # check if this unpacking assignment
            targets = assign_ast.targets
            if isinstance(assign_ast.targets[0], iterable_types):
                targets = assign_ast.targets[0].elts
                assign_ast.is_unpack = True
            # check if this multiple assignment
            elif len(assign_ast.targets) > 1:
                assign_ast.is_multi = True
        else:
            targets = [assign_ast.target]
        # determine no. of target variables assigned
        assign_ast.n_targets = len(targets)

        # determine no. of values assigned
        if isinstance(assign_ast.value, iterable_types):
            values = assign_ast.value.elts
            assign_ast.n_values = len(values)
        else:
            values = [assign_ast.value]
        assign_ast.n_values = len(values)

        # create back references in assignment targets and values
        if isinstance(assign_ast, Assign) and isinstance(
            assign_ast.targets[0], iterable_types
        ):
            assign_ast.targets[0].assign = assign_ast
        assign_ast.value.assign = assign_ast
        for child_node in targets + values:
            child_node.assign = assign_ast

    return ast


def analyze_const(ast: AST) -> AST:
    """Finds and labels constant literals in the given AST.

    Detects constant literals with the criteria:
    - Nodes of the Constant AST type.
    - List/Tuple ASTs containing or Constant nodes. Nested List/Tuples are
        allowed they contain Constant nodes. Note that the entire List/Tuple
        would be recognised as one Constant unless it is un unpacking expression.
    and annotates the constant literals with `is_constant` to `True`

    Args:
        ast:
            AST to scan and label constant literals.
    Returns:
        The given AST with the constants literals annotated with `is_constant`
    """

    # recursively walk AST to search for constants
    def walk_const(ast, part_of=None) -> AST:
        iterable_types = (List, Tuple)
        ignore_types = (Load, Store, Del)

        ast.is_constant = False
        if isinstance(ast, ignore_types):
            pass
        # part of collection but not constant, meaning collection is not constant
        elif part_of is not None and not isinstance(ast, iterable_types + (Constant,)):
            part_of.is_constant = False
        # constant if constant type and and not part of any larger collection
        elif part_of is None and isinstance(ast, Constant):
            ast.is_constant = True
        # make sure we are not unpacking from the iterable
        # otherwise elements should be recognised as constants instead
        elif isinstance(ast, iterable_types) and not (
            hasattr(ast, "assign") and ast.assign.is_unpack
        ):
            # mark child nodes as part of this collection node
            part_of = ast
            # mark this collection node as constant unless a child node overrides
            ast.is_constant = True
        # recursively inspect child nodes for constants
        for node in gast.iter_child_nodes(ast):
            walk_const(node, part_of)

    walk_const(ast)
    return ast

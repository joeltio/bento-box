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


def analyze_assign(ast: AST) -> AST:
    """Finds and Annotes assignments in the given AST with additional infomation

    Walks through the assignment nodes in given AST and annotates
    each node with the following info:
    - `n_targets`: no. of targets variables this assignments assign to.
    - `is_unpack`: Whether this assignment unpacks values from a List or Tuple.
    - `is_multi`: Whether this assignment assigns the same value to multiple variables.
    - `n_values`: no. of values this assignment attempts to assign
    - `values`: List of values this assignment attempts to assign
    - `tgts`: List of values this assignment attempts to assign.
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
        assign_ast.tgts = targets

        # determine no. of values assigned
        if isinstance(assign_ast.value, iterable_types):
            values = assign_ast.value.elts
            assign_ast.n_values = len(values)
        else:
            values = [assign_ast.value]
        assign_ast.n_values = len(values)
        assign_ast.values = values

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

    Requires `analyze_assign()` to analyze to the AST first.
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
    def walk_const(ast, part_of=None):
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


def analyze_symbol(ast: AST) -> AST:
    """Finds and labels symbols in the given AST.

    Detects symbols as:
    - Name AST nodes referencing a unqualified symbol (ie `x`).
    - Attributes AST nodes referencing a qualified symbol (ie `x.y.z`)
    and labels the top-level AST node with:
    - `is_symbol` set to whether the node is an symbol.
    - `symbol`, set to the name of symbol as string on symbol AST nodes.

    Args:
        ast:
            AST to scan and label symbols
    Returns:
        The given AST with the constants literals annotated with `is_constant`
    """
    # TODO(mrzzy): annotate `qualified_sym` set to the fully qualified name of
    # symbol on symbol AST nodes.

    # walk AST top down to label symbols to capture
    # parent Attribute node to qualifying child node relatiionships
    def walk_symbol(ast, qualifying_attrs=[]):
        # assume is not symbol unless proven otherwise
        ast.is_symbol = False
        # check if name is unqualified symbol
        if isinstance(ast, Name) and len(qualifying_attrs) == 0:
            ast.is_symbol, ast.symbol = True, ast.id
            return
        # check if name part of qualified symbol
        elif isinstance(ast, Name):
            top_attr = qualifying_attrs[0]
            top_attr.is_symbol = True
            # qualified names are written in revered
            top_attr.symbol = f"{ast.id}." + ".".join(
                [a.attr for a in reversed(qualifying_attrs)]
            )
            return
        # append qualifying attributes of a incomplete qualified symbol
        elif isinstance(ast, Attribute):
            # create a new copy of qualifying attrs with attribute appended
            qualifying_attrs = qualifying_attrs + [ast]

        # recursively inspect child nodes for constants
        for node in gast.iter_child_nodes(ast):
            walk_symbol(node, qualifying_attrs)

    walk_symbol(ast)
    return ast


def resolve_symbol(ast: AST) -> AST:
    """Resolves and labels definition of symbols in the given AST.

    Requires `analyze_symbol()` & `analyze_assign()` to analyze to the AST first.
    Tries to Resolves symbols detected by `analyze_symbol()` using definitions from:
    - Assign AST nodes
    - FunctionDef AST nodes
    and annotates the symbol nodes with `definition` set to the node that provides
    the definition for that node.
    Args:
        ast:
            AST to resolve symbols in.
    Returns:
        The given AST with to symbol nodes annotated with their definitions
    """
    # TODO(mrzzy): resolve qualified symbols, ClassDef.
    # TODO(mrzzy): support more types of assignment AnnAssign, AugAssign.
    # TODO(mrzzy): resolve Global symbol table provided by `globals()`.
    def walk_resolve(ast, symbol_table=deque([{}])):
        # get current stack frame of the symbol table
        symbol_frame = symbol_table[-1]
        new_scope = False
        if isinstance(ast, Assign):
            # update frame with definitions for symbol defined in assignment
            assign = ast
            target_syms = {t.symbol: getattr(t, "symbol", None) for t in assign.tgts}
            # create mapping of assignments made in this assign AST node
            assign_map = dict(zip(target_syms, assign.values))
            symbol_frame.update(assign_map)
        elif isinstance(ast, FunctionDef):
            # record symbol defined by function definition
            fn_def = ast
            symbol_frame[fn_def.name] = fn_def
            # record arguments defined in function as symbols
            for arg in fn_def.args.args:
                symbol_frame[arg.id] = arg
            # function definition creates a new scope
            new_scope = True
        elif hasattr(ast, "symbol"):
            # try to resolve symbol and label definition of symbol on symbol AST node
            try:
                ast.definition = symbol_frame[ast.symbol]
            except KeyError:
                pass
        # create a new stack frame if in new scope
        if new_scope:
            new_frame = dict(symbol_frame)
            symbol_table.append(new_frame)
        # recursively resolve attributes of child nodes
        for node in gast.iter_child_nodes(ast):
            walk_resolve(node, symbol_table)
        # pop stack frame from symbol table to revert to previous frame
        if new_scope:
            symbol_table.pop()

    walk_resolve(ast)
    return ast


# TODO(mrzzy): create parent edge
def analyze_parent(ast: AST) -> AST:
    """Annotate each AST node in the given AST  with its parent node.
    Labels each AST node with its parent AST node set to the `parent` attribute.
    If the AST node has no parent, the AST node would not be annotated.

    Args:
        ast:
            AST to annotate parents nodes in.
    Returns:
        The given AST with nodes annotated with their parent AST node.
    """

    def walk_parent(ast, parent=None):
        if not parent is None:
            ast.parent = parent

        # recursively resolve parents of child nodes
        for node in gast.iter_child_nodes(ast):
            walk_parent(node, ast)

    walk_parent(ast)
    return ast


# TODO(mrzzy): identify blocks (ie if/else, functiondef, classdef)
# TODO(mrzzy): activity analysis on body (ie assignments that happen)

#
# Bentobox
# SDK - Graph
# Analyzers
#

import gast
from astunparse import unparse
from copy import deepcopy

from collections import deque
from collections.abc import Iterable
from math import inf
from gast import (
    AST,
    Constant,
    List as ListAST,
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
    BinOp,
    Subscript,
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
        iterable_types = (ListAST, Tuple)
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
        iterable_types = (ListAST, Tuple)
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
    - Subscript AST nodes referencing a subscripted symbol (ie `x[y]`)
    and labels the top-level AST node with:
    - `is_symbol` set to whether the node is an symbol.
    - `symbol` set to the name of symbol as string on symbol AST nodes.
    - `base_symbol` set to the base symbol ie `x` for `x.y.z` and `x[y]`

    Args:
        ast:
            AST to scan and label symbols
    Returns:
        The given AST with the constants literals annotated with `is_constant`
    """
    # TODO(mrzzy): annotate `qualified_sym` set to the fully qualified name of
    # symbol on symbol AST nodes.

    # walk AST top down to label symbols to capture qualifier relationships
    def walk_symbol(ast, qualifiers=[], field_name=""):
        # assume is not symbol unless proven otherwise
        ast.is_symbol = False
        # check if name is unqualified symbol
        if isinstance(ast, Name) and len(qualifiers) == 0:
            ast.is_symbol, ast.symbol, ast.base_symbol = True, ast.id, ast.id
        # append qualifiers of a incomplete qualified symbol
        elif isinstance(ast, (Subscript, Attribute)):
            qualifiers = qualifiers + [ast]
        # check if name part of qualified symbol and not part of a subcript's slice
        elif isinstance(ast, Name) and field_name != "slice":
            # qualifiers are recorded in reverse order
            base_sym = symbol = ast.id
            for qualifier in reversed(qualifiers):
                if isinstance(qualifier, Attribute):
                    symbol += f".{qualifier.attr}"
                elif isinstance(qualifier, Subscript):
                    # render slice AST as source code
                    src_slice = unparse(qualifier.slice).rstrip()
                    symbol += f"[{src_slice}]"
            # label top level symbol
            top_attr = qualifiers[0]
            top_attr.is_symbol, top_attr.symbol, top_attr.base_symbol = (
                True,
                symbol,
                base_sym,
            )

        # recursively inspect child nodes for constants
        for name, value in gast.iter_fields(ast):
            # extract AST nodes from fields
            if isinstance(value, AST):
                nodes = [value]
            elif isinstance(value, Iterable) and all(
                [isinstance(v, AST) for v in value]
            ):
                nodes = value
            else:
                # non node field-skip
                continue

            for node in nodes:
                walk_symbol(node, qualifiers, field_name=name)

    walk_symbol(ast)
    return ast


def resolve_symbol(ast: AST) -> AST:
    """Resolves and labels definition of symbols in the given AST.

    Requires `analyze_symbol()` & `analyze_assign()` to analyze to the AST first.
    Tries to Resolves symbols detected by `analyze_symbol()` using definitions from:
    - Assign AST nodes
    - FunctionDef AST nodes
    and annotates the symbol nodes with `definition` set to the node that provides
    the latest definition for that node, or None if no definition can be resolved for the symbol.

    Additionally, annotates symbol nodes with `definitions` set to a list of all definitions
    resolved for that node, or an empty list of no definition can be resolved for the symbol.

    Args:
        ast:
            AST to resolve symbols in.
    Returns:
        The given AST with to symbol nodes annotated with their definitions
    """
    # TODO(mrzzy): resolve qualified symbols, ClassDef.
    # symbol table: stack of dict[symbol: list of definitions for symbol]
    def walk_resolve(ast, symbol_table=deque([{}])):
        # get current stack frame of the symbol table
        symbol_frame = symbol_table[-1]
        new_scope = False

        def push_definition(symbol_frame, target_sym, assign_value):
            # record definition (assign value) for symbol in symbol table
            definitions = symbol_frame.get(target_sym, [])
            definitions.append(assign_value)
            symbol_frame[target_sym] = definitions

        if isinstance(ast, (Assign, AnnAssign)):
            # update frame with definitions for symbol defined in assignment
            assign = ast
            target_syms = {t.symbol: getattr(t, "symbol", None) for t in assign.tgts}
            for target_sym, assign_value in zip(target_syms, assign.values):
                push_definition(symbol_frame, target_sym, assign_value)
        elif isinstance(ast, FunctionDef):
            # record symbol defined by function definition
            fn_def = ast
            push_definition(symbol_frame, target_sym=fn_def.name, assign_value=fn_def)
            # record arguments defined in function as symbols
            for arg in fn_def.args.args:
                push_definition(symbol_frame, target_sym=arg.id, assign_value=arg)
            # function definition creates a new scope
            new_scope = True
        elif hasattr(ast, "symbol"):
            # try to resolve symbol definitions
            definitions = symbol_frame.get(ast.symbol, [])
            # label latest definition of symbol on symbol AST node
            ast.definition = definitions[-1] if len(definitions) >= 1 else None
            # label all resolved definitions of symbol on symbol AST node
            ast.definitions = definitions

        # create a new stack frame if in new scope
        if new_scope:
            new_frame = deepcopy(symbol_frame)
            symbol_table.append(new_frame)
        # recursively resolve attributes of child nodes
        for node in gast.iter_child_nodes(ast):
            walk_resolve(node, symbol_table)
        # pop stack frame from symbol table to revert to previous frame
        if new_scope:
            symbol_table.pop()

    walk_resolve(ast)
    return ast


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


def analyze_block(ast: AST) -> AST:
    """Annotate each AST node in the given AST with the code block it belongs to.
    Labels each AST node with the code block it belongs to set to the `block` attribute
    and `is_block` set to `True` on code block nodes themselves.
    If the AST node is not part of any code block , the AST node would not be annotated.

    Args:
        ast:
            AST to annotate parents nodes in.
    Returns:
        The given AST with AST nodes annotated with the code block that they are part of
        and code block nodes annotated with `is_symbol`
    """

    def walk_block(ast, block=None):
        if not block is None:
            ast.block = block
        # detect code blocks by checking for attributes
        ast.is_block = any(hasattr(ast, attr) for attr in ["body", "orelse"])
        if ast.is_block:
            block = ast
        # recursively resolve code blocks of child nodes
        for node in gast.iter_child_nodes(ast):
            walk_block(node, block)

    walk_block(ast)
    return ast


def analyze_activity(ast: AST) -> AST:
    """Analyze each code block AST node for assignment and use activity.

    Requires resolve_symbol() and analyze_block() to analyze the AST first.
    Analyzes activity in each code block by identifying which symbols are used
    (input symbol) and assigned to (output symbol) in the code block.
    Input and output symbols in nested child code blocks are also considered
    to be input and output symbol of parent code blocks.

    Labels the input and output symbols by setting the `input_syms` and `output_syms`
    attributes on the code block AST to a dict with the key being the symbol name
    and the value a list the of the AST nodes where the symbol is assigned or used.
    The list of AST nodes are sorted in the order they appear in source code.

    Additionally labels the base input and output symbols by setting to the
    base version of input and output symbols `base_in_syms` and `base_out_syms`.

    Args:
        ast:
            AST to analyze and annotate code block AST nodes in.
    Returns:
        The given AST with code block nodes annotated the input and output symbols
    """
    symbols = [n for n in gast.walk(ast) if n.is_symbol]
    for symbol in symbols:
        block = symbol.block
        input_syms = getattr(block, "input_syms", {})
        output_syms = getattr(block, "output_syms", {})
        base_in_syms = getattr(block, "base_in_syms", {})
        base_out_syms = getattr(block, "base_out_syms", {})

        def add_symbol_ref(sym_dict, symbol, use_base=False):
            if use_base:
                symbol_str = symbol.base_symbol
            else:
                symbol_str = symbol.symbol

            sym_refs = sym_dict.get(symbol_str, [])
            sym_refs.append(symbol)
            # tim-sort should be relatively performant when sorting almost sorted lists
            # https://stackoverflow.com/a/23809854
            sym_refs = sorted(sym_refs, key=(lambda ast: (ast.lineno, ast.col_offset)))
            sym_dict[symbol_str] = sym_refs
            return sym_dict

        # detect input symbol by checking symbol context and that its declared outside code block
        if (
            isinstance(symbol.ctx, Load)
            and symbol.definition is not None
            and any(sym_def.block != block for sym_def in symbol.definitions)
        ):
            input_syms = add_symbol_ref(input_syms, symbol)
            base_in_syms = add_symbol_ref(base_in_syms, symbol, use_base=True)
        # detect output symbol by checking symbol context
        elif isinstance(symbol.ctx, (Store, Del)):
            output_syms = add_symbol_ref(output_syms, symbol)
            base_out_syms = add_symbol_ref(base_out_syms, symbol, use_base=True)
        block.input_syms, block.output_syms = input_syms, output_syms
        block.base_in_syms, block.base_out_syms = base_in_syms, base_out_syms

    # walk the AST bottom up to propagate symbol activity to parent code blocks
    def propagate_activity(ast):
        # recursively obtain symbol activity from child code blocks
        input_syms, output_syms, base_in_syms, base_out_syms = {}, {}, {}, {}
        for node in gast.iter_child_nodes(ast):
            (
                child_inputs,
                child_outputs,
                child_base_ins,
                child_base_outs,
            ) = propagate_activity(node)
            input_syms.update(child_inputs)
            output_syms.update(child_outputs)
            base_in_syms.update(child_base_ins)
            base_out_syms.update(child_base_outs)

        if not ast.is_block:
            return input_syms, output_syms, base_in_syms, base_out_syms
        # include symbol activity from this blockf
        block = ast
        input_syms.update(getattr(ast, "input_syms", {}))
        output_syms.update(getattr(ast, "output_syms", {}))
        base_in_syms.update(getattr(ast, "base_in_syms", {}))
        base_out_syms.update(getattr(ast, "base_out_syms", {}))
        block.input_syms, block.output_syms = input_syms, output_syms
        block.base_in_syms, block.base_out_syms = base_in_syms, base_out_syms

        return input_syms, output_syms, base_in_syms, base_out_syms

    propagate_activity(ast)
    return ast

#
# Bentobox
# SDK - Graph
# AST Utils
#


import gast

from tempfile import NamedTemporaryFile
from astunparse import unparse
from importlib.util import spec_from_file_location, module_from_spec
from gast import (
    AST,
    Call,
    FunctionDef,
    keyword,
    arguments,
    Return,
    Tuple,
    Name,
    Load,
    Store,
    Del,
    Attribute,
    Param,
    Assign,
    List as ListAST,
    If,
    Constant,
)
from inspect import getsource, getsourcefile
from textwrap import dedent
from typing import Any, Dict, Optional, List, Union


def parse_ast(obj: Any) -> AST:
    """Parse the AST of the given `obj`.
    Annotates the AST with the AST of the entire source file in which `obj` is defined in.

    Args:
        obj: Object to obtain AST for. Can be any object supported by `inspect.getsource()`.

    Returns:
        The AST parsed from the the given `obj`. Entire source AST can be accessed via `src_ast` attribute.
    """
    src = getsource(obj)
    clean_src = dedent(src)
    return gast.parse(clean_src)


def name_ast(name: str, ctx: Union[Load, Store, Del] = Load()) -> Name:
    """Convenience function for creating Name AST nodes

    Args:
        name: Maps to the `id` parameter of the Name constructor.
        ctx: Maps to the `id` parameter of the Name constructor.
    """
    return Name(id=name, ctx=ctx, annotation=None, type_comment="")


def assign_ast(
    targets: List[AST], values: List[AST], multi_assign: bool = False
) -> AST:
    """Convenience function for creating Assignment AST

    Args:
        targets: List of target AST nodes to assign to.
        values: List of values as AST nodes to assign to the target nodes.
        multi_assign: Whether to assign multiple targets to the same value
    """
    if len(targets) >= 2:
        targets = targets if multi_assign else [Tuple(elts=targets, ctx=Store())]
    return Assign(
        targets=targets,
        value=values[0] if len(values) == 1 else Tuple(elts=values, ctx=Load()),
    )


def call_func_ast(
    fn_name: str,
    args: Union[List[AST], Dict[str, AST]] = [],
    attr_parent: Optional[str] = None,
) -> Call:
    """Call the Function with the given name with the given args.

    Applies the arguments in `args` by argument name in to `fn` and calls the
    function by creating a Call AST node. Any extra arguments in `args` not used
    to apply arguments in `fn` is ignored.

    Args:
        fn: FunctionDef AST of the function to call.
        args: Mapping of argument name to argument value to apply function call.
        attr_parent: Optionally specify name of the parent attribute required
            to reference the given `fn`. Genrates a call with `attr_parent.fn(...)`.
    Returns:
        Call AST with the given args applied that represents the function call.
    """
    # create qualified reference to function
    if attr_parent is not None:
        func_ref = Attribute(
            value=name_ast(attr_parent),
            attr=fn_name,
            ctx=Load(),
        )
    else:
        func_ref = name_ast(fn_name)
    # create call AST with function name and apply args
    if isinstance(args, dict):
        return Call(
            args=[],
            func=func_ref,
            keywords=[keyword(name, value) for name, value in args.items()],
        )
    # apply arguments using positional arguments syntax
    return Call(args=args, func=func_ref, keywords=[])


def wrap_func_ast(
    name: str,
    args: List[str],
    block: List[AST],
    returns: List[str] = [],
    return_tuple: bool = False,
) -> FunctionDef:
    """Wrap the given code block in a function as a FunctionDef AST node.

    Args:
        name: The name of the function wrapping the block of code.
        args: List of argument names which the wrapping function accepts
        block:
            List of AST nodes reprsenting the code block being wrapped by the
            wrapping function. The code block should not contain `return` statements
        returns: List of variable names to return from the wrapping functions.
        return_tuple:
            Whether to force the wrapping function to return to be a tuple,
            irregardless of whether multiple values are actually returned.
    Returns:
        The created function wrapping the given code block.
    """
    # append return statement if actually returning variables
    if len(returns) > 0:
        # convert return names to return AST node
        return_ast = Return(
            value=[Tuple(elts=[name_ast(r) for r in returns], ctx=Load())]
            if len(returns) > 1 or return_tuple
            else name_ast(returns[0])
        )
        block = block + [return_ast]

    return FunctionDef(
        name=name,
        args=arguments(
            args=[name_ast(a, Param()) for a in args],
            defaults=[],
            posonlyargs=[],
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            vararg=None,
        ),
        body=block,
        decorator_list=[],
        returns="",
        type_comment="",
    )


def wrap_block_ast(
    block: List[AST],
) -> AST:
    """Wraps the given code block in a always true If AST node.

    Allows the list of statements of the code block to be represented by a single AST node.
    Without altering the function of the code within code block.

    Args:
        block: List of AST nodes representing the statements in the code block.
    Returns:
        If AST node wrapping the code block.
    """
    return If(
        test=Constant(value=True, kind=None),
        body=block,
        orelse=[],
    )


def load_ast_module(ast: AST) -> Any:
    # TODO(mrzzy): docs
    src = unparse(ast)
    with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(src)
        f.flush()
        # import the source as a module
        mod_spec = spec_from_file_location("compiled", f.name)
        module = module_from_spec(mod_spec)
        mod_spec.loader.exec_module(module)

    return module

#
# Bentobox
# SDK - Graph
# AST Utils
#


import gast

from tempfile import NamedTemporaryFile
from astunparse import unparse
from importlib.util import spec_from_file_location, module_from_spec
from gast import AST, Call, FunctionDef, keyword, Name, Load, Attribute
from inspect import getsource, cleandoc
from textwrap import dedent
from typing import Any, Dict, Optional


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


def parse_ast(obj: Any) -> AST:
    """Parse the AST of the given `obj`.

    Args:
        obj: Object to obtain AST for. Can be any object supported by `inspect.getsource()`.

    Returns:
        The AST parsed from the the given `obj`
    """
    src = getsource(obj)
    clean_src = dedent(src)
    return gast.parse(clean_src)


def call_func_ast(
    fn: FunctionDef, args: Dict[str, Any], attr_parent: Optional[str] = None
) -> Call:
    """Call the Function with the given FunctionDef AST  with the given args.

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
    # collect names of parameters from fn_call
    param_names = set(param.id for param in fn.args.args)
    # extract arguments and apply to params
    apply_arg = {name: args[name] for name in param_names}
    # create qualified reference to function
    if attr_parent is not None:
        func_ref = Attribute(
            value=Name(id=attr_parent, ctx=Load(), annotation=None, type_comment=""),
            attr=fn.name,
            ctx=Load(),
        )
    else:
        func_ref = Name(id=fn.name, ctx=Load(), annotation=None, type_comment="")
    # create call AST with function name and apply args
    return Call(
        args=[],
        func=func_ref,
        keywords=[keyword(name, value) for name, value in apply_arg.items()],
    )


def load_ast_module(ast: AST) -> Any:
    # TODO(mrzzy) docs
    src = unparse(ast)
    with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(src)
        f.flush()
        # import the source as a module
        mod_spec = spec_from_file_location("compiled", f.name)
        module = module_from_spec(mod_spec)
        mod_spec.loader.exec_module(module)

    return module

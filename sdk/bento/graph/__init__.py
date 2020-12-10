#
# Bentobox
# SDK - Graph
#

import gast

from gast import FunctionDef, AST
from inspect import getsource
from textwrap import dedent
from typing import Callable, List
from astunparse import unparse
from tempfile import NamedTemporaryFile
from importlib.util import spec_from_file_location, module_from_spec

from bento.graph.analyzers import analyze_func, analyze_convert_fn
from bento.graph.ast import parse_ast
from bento.graph.plotter import Plotter
from bento.protos.graph_pb2 import Graph, Node


Linter = Callable[[AST], None]
Transform = Callable[[AST], AST]
Analyzer = Callable[[AST], AST]


def compile_graph(
    convert_fn: Callable,
    analyzers: List[Analyzer] = [
        analyze_func,
        analyze_convert_fn,
    ],
    linters: List[Linter] = [],
    transforms: List[Transform] = [],
) -> Graph:
    """Compiles the given `convert_fn` into a computation Graph.

    Compiles by converting the given `convert_fn` function to AST,
    applying given `analyzers` on the AST to perform static analysis,
    linting the AST with the given `linters` to perform static checks,
    applying the given `transforms` to transform the AST.

    The transformed AST is converted back to source where it can be imported
    to provide a compiled function that builds the graph using the given `Plotter` on call.
    The graph obtained from the `Plotter` is finally returned.

    The analyzers and transforms that should be used should be preconfigured.
    Users should simply annotate the function they want converted with `@compile_graph`

    Example:
        @compile_graph
        def convert_fn(g: Plotter):
            # ...

    Args:
        convert_fn:
            Target function containing the source to convert to the computation graph.
            The function should take in one parameter: a `Plotter` instance which
            allows users to access graphing specific operations.
        analyzers:
            List of `Analyzer`s that are run sequentially on the AST perform static analysis.
        linters:
            List of `Linter`s that are run sequentially on the AST to perform
            static checks on the convertablity of the AST. `Linter`s are expected
            to throw exception when failing a check.
        transforms:
            List of `Transform`s that are run sequentially to transform the AST to
            a compiled function (in AST form) that builds the computation graph when called.

    Returns:
        The converted computational Graph as a `Graph` protobuf message.
    """

    # parse ast from function source
    ast = parse_ast(convert_fn)

    # apply analyzers to conduct static analysis
    for analyzer in analyzers:
        ast = analyzer(ast)
    # check that AST can be coverted by applying linters to check convertablity
    for linter in linters:
        linter(ast)
    # convert AST to computation graph by applying transforms
    for transform in transforms:
        ast = transform(ast)
    # TODO: move to transforms
    ast.body[0].decorator_list = []
    ast.body[0].name = "build_graph"

    # parse AST back to source and write to file
    src = unparse(ast)
    with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(src)
        f.flush()
        # import the source as a module
        mod_spec = spec_from_file_location("compiled", f.name)
        compiled = module_from_spec(mod_spec)
        mod_spec.loader.exec_module(compiled)

    # run build graph function with plotter to build final computation graph
    g = Plotter()
    compiled.build_graph(g)
    return g.graph()
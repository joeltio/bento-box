#
# Bentobox
# SDK - Graph
#

import gast

from gast import FunctionDef, AST
from textwrap import dedent
from typing import Callable, List

from bento.graph.analyzers import (
    analyze_func,
    analyze_convert_fn,
    analyze_symbol,
    analyze_assign,
    resolve_symbol,
    analyze_parent,
    analyze_block,
    analyze_activity,
)
from bento.graph.transforms import (
    transform_build_graph,
    transform_ternary,
    transform_ifelse,
)
from bento.graph.ast import parse_ast, load_ast_module
from bento.graph.plotter import Plotter
from bento.protos.graph_pb2 import Graph, Node


Analyzer = Callable[[AST], AST]
Linter = Callable[[AST], None]
Transform = Callable[[AST], AST]


def compile_graph(
    convert_fn: Callable,
    analyzers: List[Analyzer] = [
        analyze_parent,
        analyze_func,
        analyze_convert_fn,
        analyze_symbol,
        analyze_assign,
        resolve_symbol,
        analyze_block,
        analyze_activity,
    ],
    linters: List[Linter] = [],
    transforms: List[Transform] = [
        transform_build_graph,
        transform_ternary,
        transform_ifelse,
    ],
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
        def car_pos_graph(g: Plotter):
            car = g.entity(
                components=[
                    "position",
                ]
            )
            env = g.entity(components=["clock"])
            x_delta = 20 if env["clock"].tick_ms > 2000 else 10
            car["position"].x = x_delta

        # use compiled graph 'car_pos_graph' in code ...

    Args:
        convert_fn: Target function containing the source to convert to the computation graph.
            The function should take in one parameter: a `Plotter` instance which
            allows users to access graphing specific operations. Must be a plain Python
            Function, not a Callable class, method, classmethod or staticmethod.
        analyzers: List of `Analyzer`s that are run sequentially on the AST perform static analysis.
            Analyzers can add attributes to AST nodes but not modify the AST tree.
        linters: List of `Linter`s that are run sequentially on the AST to perform
            static checks on the convertability of the AST. `Linter`s are expected
            to throw exception when failing a check.
        transforms: List of `Transform`s that are run sequentially to transform the AST to
            a compiled function (in AST form) that builds the computation graph when called.

    Returns:
        The converted computational Graph as a `Graph` protobuf message.
    """

    # parse ast from function source
    ast = parse_ast(convert_fn)

    # apply analyzers to conduct static analysis
    for analyzer in analyzers:
        ast = analyzer(ast)
    # check that AST can be coverted by applying linters to check convertability
    for linter in linters:
        linter(ast)
    # convert AST to computation graph by applying transforms
    for transform in transforms:
        ast = transform(ast)

    # load AST back as a module
    compiled = load_ast_module(ast)
    # run build graph function with plotter to build final computation graph
    g = Plotter()
    compiled.build_graph(g)
    return g.graph()

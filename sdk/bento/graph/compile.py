#
# Bentobox
# SDK - Graph
#

import gast

from gast import FunctionDef, AST
from textwrap import dedent
from typing import Callable, List

from bento.sim import Simulation
from bento.ecs.graph import GraphEntity
from bento.graph.preprocessors import preprocess_augassign
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
    platform: Simulation,
    preprocessors: List[Transform] = [
        preprocess_augassign,
    ],
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
    """Compiles the given `convert_fn` into a computation Graph running the given sim.

    Use by annotating the target `convert_fn` should be with `@compile_graph(sim)` to compile.

    The target `convert_fn` should take in one parameter: a `Plotter` instance which
    allows users to access graphing specific operations. Must be a plain Python
    Function, not a Callable class, method, classmethod or staticmethod.

    When compiling the computational graph, the ECS entities & components on the
    given `Simulation` platform are available for use in `convert_fn` in the form
    of `GraphEntity` and `GraphComponent` respectively.

    Globals can be used read only in the `convert_fn`. Writing to globals is not supported.

    Compiles by converting the given `convert_fn` function to AST
    applying the given `preprocessors` transforms to perform preprocessing on the AST,
    applying given `analyzers` on the AST to perform static analysis,
    linting the AST with the given `linters` to perform static checks,
    applying the given `transforms` to transform the AST to a function that
    plots the computational graph when run.

    Note:
        Even though both `preprocessors` and `transforms` are comprised of  a list of `Transform`s
        `preprocessors` transforms are applied before any static analysis is done while
        `transforms` are applied after static analysis. This allows `preprocessors` to focus
        on transforming the AST to make static analysis easier while `transforms` to focus on
        transforming the AST to plot a computation graph.

    The transformed AST is converted back to source where it can be imported
    to provide a compiled function that builds the graph using the given `Plotter` on call.
    The graph obtained from the `Plotter` is finally returned.

        Example:
        @compile_graph(sim)
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
        platform: Target simulation as the target platform for the compiled computation graph
            to run on. Provides the ECS entity and components available for use in `convert_fn`.

        preprocessors: List of `Transform`s that are run sequentially to apply
            preprocesssing transforms to the AST before any static analysis is done.
            Typically these AST transforms make static analysis easier by simplifying the AST.

        analyzers: List of `Analyzer`s that are run sequentially on the AST perform
            static analysis.  Analyzers can add attributes to AST nodes but not
            modify the AST tree.

        linters: List of `Linter`s that are run sequentially on the AST to perform
            static checks on the convertability of the AST. `Linter`s are expected
            to throw exception when failing a check.

        transforms: List of `Transform`s that are run sequentially to transform the
            AST to a compiled function (in AST form) that builds the computation
            graph when called.

    Returns:
        The converted computational Graph as a `Graph` protobuf message.
    """

    def _compile_graph(convert_fn: Callable):
        # parse ast from function source
        ast = parse_ast(convert_fn)

        # apply preprocessors to apply preprocesssing transforms on the AST
        for preprocessor in preprocessors:
            ast = preprocessor(ast)

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
        # allow the use of globals symbols with respect to convert_fn function
        # to be used during graph plotting
        compiled.build_graph.__globals__.update(convert_fn.__globals__)
        # unpack available Entities and components from target platform available for
        # use during graph plotting.
        graph_entities = [
            GraphEntity([c.component_name for c in e.components], e.id)
            for e in platform.entities
        ]

        # run build graph function with plotter to build final computation graph
        g = Plotter(entities=graph_entities)
        compiled.build_graph(g)
        return g.graph()

    return _compile_graph

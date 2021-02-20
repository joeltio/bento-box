#
# Bentobox
# SDK - Graph
#

import os
from textwrap import dedent
from typing import Callable, List

from bento.spec.ecs import ComponentDef, EntityDef
from bento.graph.analyzers import (
    analyze_activity,
    analyze_assign,
    analyze_block,
    analyze_convert_fn,
    analyze_func,
    analyze_parent,
    analyze_symbol,
    resolve_symbol,
)
from bento.graph.ast import load_ast_module, parse_ast
from bento.graph.plotter import Plotter
from bento.graph.preprocessors import preprocess_augassign
from bento.spec.graph import Graph
from bento.graph.transforms import (
    transform_build_graph,
    transform_ifelse,
    transform_ternary,
)
import gast
from gast import AST


Analyzer = Callable[[AST], AST]
Linter = Callable[[AST], None]
Transform = Callable[[AST], AST]
ConvertFn = Callable[[Plotter], None]


def compile_graph(
    convert_fn: ConvertFn,
    entity_defs=List[EntityDef],
    component_defs=List[ComponentDef],
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
        def car_pos_fn(g: Plotter):
            car = g.entity(
                components=[
                    "position",
                ]
            )
            env = g.entity(components=["clock"])
            x_delta = 20 if env["clock"].tick_ms > 2000 else 10
            car["position"].x = x_delta

        car_pos_graph = compile_graph(car_pos_fn, entity_defs, component_defs)
        # use compiled graph 'car_pos_graph' in code ...

    Args:
        convert_fn: Function containing the code that should be compiled into a computational graph.
            The target `convert_fn` should take in one parameter: a `Plotter` instance which
            allows users to access graphing specific operations. Must be a plain Python
            Function, not a Callable class, method, classmethod or staticmethod.

        entity_defs: List of EntityDef representing the ECS entities available for
            use in `convert_fn` via the Plotter instance.

        component_defs: List of ComponentDef representing the ECS component types
            available for use in `convert_fn` via the Plotter instance.

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
        The converted computational Graph as a `Graph`.
    """

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
    compiled, src_path = load_ast_module(ast, remove_src=False)
    # allow the use of globals symbols with respect to convert_fn function
    # to be used during graph plotting
    compiled.build_graph.__globals__.update(convert_fn.__globals__)  # type: ignore

    # run build graph function with plotter to build final computation graph
    g = Plotter(entity_defs, component_defs)
    try:
        compiled.build_graph(g)
    except Exception as e:
        print(f"Compilation generated source code with errors: {src_path}")
        raise e

    # remove the intermediate source file generated by load_ast_module()
    os.remove(src_path)
    return g.graph()

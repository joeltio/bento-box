#
# Bentobox
# SDK - Graph
# Tests
#

import numpy as np
from astunparse import unparse
from unittest.mock import Mock
from bento.graph.ast import parse_ast, load_ast_module
from bento.graph.plotter import Plotter
from bento.graph.analyzers import *
from bento.graph.transforms import *


def test_transform_build_graph():
    def convert_fn(g: Plotter):
        pass

    def convert_fn_with_long_name(g: Plotter):
        pass

    identity = lambda fn: fn

    @identity
    def convert_fn_with_annotation(g: Plotter):
        pass

    # convert fn test cases
    convert_fns = [
        convert_fn,
        convert_fn_with_long_name,
        convert_fn_with_annotation,
    ]

    req_analyzers = [
        analyze_func,
        analyze_convert_fn,
    ]

    for convert_fn in convert_fns:
        ast = parse_ast(convert_fn)
        for analyzer in req_analyzers:
            ast = analyzer(ast)
        trans_ast = transform_build_graph(ast)

        # try running the transformed function renamed to 'build_graph'
        mod = load_ast_module(trans_ast)
        mod.build_graph(Plotter())


# transform ternary expressions into plotting switch nodes
def test_transform_ternary():
    def ternary_fn(g: Plotter):
        int_ternary = 1 if True else 2

    req_analyzers = [
        analyze_func,
        analyze_convert_fn,
    ]
    ast = parse_ast(ternary_fn)
    for analyzer in req_analyzers:
        ast = analyzer(ast)
    trans_ast = transform_build_graph(transform_ternary(ast))

    mod = load_ast_module(trans_ast)
    mock_g = Mock(wraps=Plotter())
    mod.build_graph(mock_g)
    mock_g.switch.assert_called_once_with(
        condition=True,
        true=1,
        false=2,
    )

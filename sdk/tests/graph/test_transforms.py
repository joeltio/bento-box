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
        mod.build_graph(Plotter(()))


# test transformation of ternary expressions into plotting switch nodes
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


# test transformations of ifelse statements into plotting switch nodes
def test_tranform_ifelse():
    def if_fn(g: Plotter):
        x, w = "str1", "str2"
        if True:
            x = w

    def ifelse_fn(g: Plotter):
        w, y = "str1", "str2"
        if True:
            x = w
            z = 1
        else:
            x = y
            z = 2

    def ifelse_elif_fn(g: Plotter):
        y, m, n = "str1", "str2", "str3"
        if True:
            x = y
            z = 1
        elif False:
            x = m
            z = 2
        else:
            x = n
            z = 3

    def if_augassign_fn(g: Plotter):
        x = 1
        if True:
            x = x + 1
        else:
            x = x + 2

    req_analyzers = [
        analyze_func,
        analyze_convert_fn,
        analyze_assign,
        analyze_symbol,
        resolve_symbol,
        analyze_block,
        analyze_activity,
    ]

    # test case plotter => expected g.switch() call args
    g = Plotter()
    ifelse_fns = [
        (
            if_fn,
            [
                {"condition": True, "true": "str2", "false": "str1"},
            ],
        ),
        (
            ifelse_fn,
            [
                {"condition": True, "true": "str1", "false": "str2"},
                {"condition": True, "true": 1, "false": 2},
            ],
        ),
        (
            ifelse_elif_fn,
            [
                {
                    "condition": True,
                    "true": "str1",
                    "false": g.switch(False, "str2", "str3"),
                },
                {"condition": True, "true": 1, "false": g.switch(False, 2, 3)},
                {"condition": False, "true": "str2", "false": "str3"},
                {"condition": False, "true": 2, "false": 3},
            ],
        ),
        (
            if_augassign_fn,
            [
                {"condition": True, "true": 2, "false": 3},
            ],
        ),
    ]

    for fn, expected_switch_args in ifelse_fns:
        ast = parse_ast(fn)
        for analyzer in req_analyzers:
            ast = analyzer(ast)
        trans_ast = transform_build_graph(transform_ifelse(ast))

        mod = load_ast_module(trans_ast)
        mock_g = Mock(wraps=Plotter())
        mod.build_graph(mock_g)

        for expected_arg in expected_switch_args:
            mock_g.switch.assert_any_call(**expected_arg)

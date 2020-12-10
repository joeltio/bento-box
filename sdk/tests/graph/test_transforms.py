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
from bento.graph.transforms import transform_const

# test that constants are replaced with constant nodes
def test_transform_const():
    def convert_fn(g):
        int_const = 2
        float_const = 3.14
        str_const = "str"
        list_const = [1, 2, 3]
        tuple_const = (1, 2, 3)
        multiassign_a, multiassign_b = True, False

    req_analyzers = [
        analyze_func,
        analyze_convert_fn,
        analyze_assign,
        analyze_const,
    ]
    ast = parse_ast(convert_fn)
    for analyzer in req_analyzers:
        ast = analyzer(ast)
    trans_ast = transform_const(ast)
    # check transformation worked by inspecting mocked plotter is called
    # to create the create the correct constant nodes.
    mod = load_ast_module(trans_ast)
    mock_g = Mock(wraps=Plotter())
    mod.convert_fn(mock_g)
    for expected_val in [2, 3.14, "str", [1, 2, 3], (1, 2, 3), True, False]:
        mock_g.const.assert_any_call(value=expected_val)

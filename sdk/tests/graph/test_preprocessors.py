#
# Bentobox
# SDK - Graph
# Preprocessor Tests
#

import gast
from unittest.mock import Mock
from bento.graph.ast import parse_ast
from bento.graph.plotter import Plotter
from bento.graph.preprocessors import *


def test_preprocess_augassign():
    # test cases: line 2 is input AST, line 3 is expected output AST
    def add_augassign_fn():
        x, y = 1, 2
        x += y
        x = x + y

    def sub_augassign_fn():
        x, y = 1, 2
        x -= y
        x = x - y

    def mul_augassign_fn():
        x, y = 1, 2
        x *= y
        x = x * y

    def div_augassign_fn():
        x, y = 1, 2
        x /= y
        x = x / y

    class C:
        x = 1

    def attribute_augassign_fn():
        y = 1, 2
        C.x /= y
        C.x = C.x / y

    augassign_fns = [
        add_augassign_fn,
        sub_augassign_fn,
        mul_augassign_fn,
        div_augassign_fn,
        attribute_augassign_fn,
    ]

    for fn in augassign_fns:
        fn_ast = parse_ast(fn).body[0]
        aug_ast, expected_ast = fn_ast.body[1], fn_ast.body[2]
        actual_ast = preprocess_augassign(aug_ast)
        assert gast.dump(actual_ast) == gast.dump(expected_ast)

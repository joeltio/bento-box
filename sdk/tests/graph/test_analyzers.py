#
# Bentobox
# SDK - Graph
# Analyzers Test
#

import gast

from bento.graph.ast import parse_ast
from bento.graph.analyzers import *

# gets the functiondef node from the given parsed ast
get_fn_ast = lambda ast: ast.body[0]

# test functiondef analyzer
def test_analyze_func():
    # test empty function detection
    def empty_fn_pass():
        pass

    def empty_fn_docstr():
        """
        docs for empty function
        """

    def empty_fn_docstr_pass():
        """
        docs for empty function
        """
        pass

    empty_fns = [
        empty_fn_pass,
        empty_fn_docstr,
        empty_fn_docstr_pass,
    ]
    fn_asts = [parse_ast(f) for f in empty_fns]
    analyzed_asts = [analyze_func(ast) for ast in fn_asts]
    assert all([get_fn_ast(ast).is_empty for ast in analyzed_asts])

    # test analyze func can detect number of arguments
    def multi_args(a, b, c=2):
        pass

    n_arg_fns = [
        (0, empty_fn_pass),
        (3, multi_args),
    ]
    fn_asts = [parse_ast(f[1]) for f in n_arg_fns]
    analyzed_asts = [analyze_func(ast) for ast in fn_asts]
    assert [
        get_fn_ast(ast).n_args == expected_n_arg[0]
        for ast, expected_n_arg in zip(analyzed_asts, n_arg_fns)
    ]

    # test docstring detection
    analyzed_ast = analyze_func(parse_ast(empty_fn_docstr))
    assert get_fn_ast(analyzed_ast).has_docstr

    # test generator detection
    def gen_fn():
        yield 2

    analyzed_ast = analyze_func(parse_ast(gen_fn))
    assert get_fn_ast(analyzed_ast).is_generator


# test nesting analyzer
def test_nesting_analyzer():
    def top_fn():
        class MiddleClass:
            def middle_fn(self):
                def bottom_fn():
                    pass

    analyzed_ast = analyze_nesting(parse_ast(top_fn))
    ast = get_fn_ast(analyzed_ast)
    expected_nest = 0
    while ast.body == [Pass()]:
        assert ast.n_nesting == expected_nest
        ast = ast.body[0]
        expected_nest += 1


# test convert fn analyzer
def test_convert_fn_analyzer():
    class NotConvertFn:
        def still_not_convert_fn(g):
            pass

    def convert_fn(g):
        pass

    convert_fns = [
        (NotConvertFn, False),
        (convert_fn, True),
    ]

    analyzed_asts = [
        analyze_convert_fn(analyze_nesting(parse_ast(f[0]))) for f in convert_fns
    ]
    assert all(
        [
            ast.missing_convert_fn != expected_fn[0]
            for ast, expected_fn in zip(analyzed_asts, convert_fns)
        ]
    )

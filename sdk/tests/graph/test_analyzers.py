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

    def nonempty_fn():
        print()

    # test cases => whether the function is expected to be empty
    empty_fns = [
        (empty_fn_pass, True),
        (empty_fn_docstr, True),
        (empty_fn_docstr_pass, True),
        (nonempty_fn, False),
    ]
    for fn, expected_empty in empty_fns:
        fn_ast = parse_ast(fn)
        analyzed_ast = analyze_func(fn_ast)
        assert get_fn_ast(analyzed_ast).is_empty == expected_empty

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
    assert get_fn_ast(analyzed_ast).docstr is not None

    # test generator detection
    def gen_fn():
        yield 2

    analyzed_ast = analyze_func(parse_ast(gen_fn))
    assert get_fn_ast(analyzed_ast).is_generator


# test convert fn analyzer
def test_convert_fn_analyzer():
    class NotConvertFn:
        def still_not_convert_fn(self):
            pass

    def convert_fn(g):
        pass

    convert_fns = [
        (NotConvertFn, False),
        (convert_fn, True),
    ]
    analyzed_asts = [
        analyze_convert_fn(analyze_func(parse_ast(f[0]))) for f in convert_fns
    ]

    def check_ast(fn_ast, expected_fn):
        assert (fn_ast is not None) == expected_fn[1]
        if fn_ast is not None:
            assert fn_ast.plotter_name == fn_ast.args.args[0].id

    for ast, expected_fn in zip(analyzed_asts, convert_fns):
        check_ast(ast.convert_fn, expected_fn)

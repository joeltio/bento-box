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


# test assign analyzer annotates assignments
def test_assign_analyzer():
    def single_assign():
        x = 2

    def multi_assign():
        a = b = True

    def unpack_assign():
        x, y = 1, 2

    assign_fns = [
        (
            single_assign,
            {"n_targets": 1, "n_values": 1, "is_unpack": False, "is_multi": False},
        ),
        (
            multi_assign,
            {"n_targets": 2, "n_values": 1, "is_unpack": False, "is_multi": True},
        ),
        (
            unpack_assign,
            {"n_targets": 2, "n_values": 2, "is_unpack": True, "is_multi": False},
        ),
    ]

    assign_types = (
        Assign,
        AnnAssign,
        AugAssign,
    )
    analyzed_asts = [analyze_assign(parse_ast(f[0])) for f in assign_fns]
    for ast, assign_fn in zip(analyzed_asts, assign_fns):
        assign_ast = [n for n in gast.walk(ast) if isinstance(n, assign_types)][0]

        # check ast has expected annotations
        _, expected_annotations = assign_fn
        assert all(
            [
                getattr(assign_ast, name) == value
                for name, value in expected_annotations.items()
            ]
        )

        # TODO(mrzzy): check backreferences are set correctly


# test that constants picked up & labeled by constants analyzer
def test_const_analyzer():
    def convert_fn(g):
        int_const = 2
        float_const = 3.14
        str_const = "str"
        list_const = [1, 2, 3]
        tuple_const = (1, 2, 3)
        boolean_const, boolean_const_2 = True, False

    req_analyzers = [
        analyze_func,
        analyze_convert_fn,
        analyze_assign,
    ]
    ast = parse_ast(convert_fn)
    for analyzer in req_analyzers:
        ast = analyzer(ast)
    analyzed_ast = analyze_const(ast)
    fn_ast = analyzed_ast.convert_fn
    get_const_ast = lambda i: fn_ast.body[i].value
    expected_asts = set(
        [get_const_ast(i) for i in range(5)]
        + [const for const in fn_ast.body[5].value.elts]
    )
    const_asts = set([n for n in gast.walk(ast) if n.is_constant])
    assert const_asts == expected_asts


# test that qualified and unqualified symbols and be detected by symbol analyzer
def test_symbol_analyzer():
    def convert_fn(g):
        x = 2
        a.b.c = "str"

    req_analyzers = [
        analyze_func,
        analyze_convert_fn,
    ]
    ast = parse_ast(convert_fn)
    for analyzer in req_analyzers:
        ast = analyzer(ast)
    analyzed_ast = analyze_symbol(ast)
    fn_ast = analyzed_ast.convert_fn
    first_id, second_id = [fn_ast.body[i].targets[0] for i in range(2) ]
    first_val, second_val = [fn_ast.body[i].value for i in range(2) ]

    # both targets should be labeled as symbols
    assert first_id.is_symbol and first_id.symbol == "x"
    assert second_id.is_symbol and second_id.symbol == "a.b.c"
    assert not first_val.is_symbol and not second_val.is_symbol

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
            {
                "n_targets": 1,
                "n_values": 1,
                "is_unpack": False,
                "is_multi": False,
                "values": [2],
                "tgts": ["x"],
            },
        ),
        (
            multi_assign,
            {
                "n_targets": 2,
                "n_values": 1,
                "is_unpack": False,
                "is_multi": True,
                "values": [True],
                "tgts": ["a", "b"],
            },
        ),
        (
            unpack_assign,
            {
                "n_targets": 2,
                "n_values": 2,
                "is_unpack": True,
                "is_multi": False,
                "values": [1, 2],
                "tgts": ["x", "y"],
            },
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
        for name, expected_value in expected_annotations.items():
            value = getattr(assign_ast, name)
            # for tgts & values, directly check name match instead of comparing ast node
            if name == "tgts":
                tgts = value
                assert [t.id for t in tgts] == expected_value
            elif name == "values":
                values = value
                assert [v.value for v in values] == expected_value
            else:
                value == expected_value
        # TODO(mrzzy): check backreferences are set correctly


# test that constants picked up & labeled by constants analyzer
def test_const_analyzer():
    def const_fn(g):
        int_const = 2
        float_const = 3.14
        str_const = "str"
        list_const = [1, 2, 3]
        tuple_const = (1, 2, 3)
        boolean_const, boolean_const_2 = True, False

    ast = parse_ast(const_fn)
    analyzed_ast = analyze_const(analyze_assign(ast))
    fn_ast = analyzed_ast.body[0]
    get_const_ast = lambda i: fn_ast.body[i].value
    expected_asts = set(
        [get_const_ast(i) for i in range(5)]
        + [const for const in fn_ast.body[5].value.elts]
    )
    const_asts = set([n for n in gast.walk(ast) if n.is_constant])
    assert const_asts == expected_asts


# test that qualified and unqualified symbols and be detected by symbol analyzer
def test_symbol_analyzer():
    def symbol_fn():
        x = 2
        a.b.c = "str"
        # TODO: multiple assign symbol
        y, z = True, False

    ast = parse_ast(symbol_fn)
    analyzed_ast = analyze_symbol(ast)
    fn_ast = analyzed_ast.body[0]
    x_target, abc_target = [fn_ast.body[i].targets[0] for i in range(2)]
    x_value, abc_value = [fn_ast.body[i].value for i in range(2)]
    y_target, z_target = fn_ast.body[2].targets[0].elts
    y_value, z_value = fn_ast.body[2].value.elts

    # targets should be labeled as symbols
    assert x_target.is_symbol and x_target.symbol == "x"
    assert abc_target.is_symbol and abc_target.symbol == "a.b.c"
    assert y_target.is_symbol and y_target.symbol == "y"
    assert z_target.is_symbol and z_target.symbol == "z"
    assert all([not val.is_symbol for val in [x_value, abc_value, y_value, z_value]])


# test that the definition of the symbol can be resolved
def test_symbol_resolution():
    def simple_fn():
        simple = 2
        simple

    def multi_assign():
        multi_a, multi_b = True, False
        multi_a, multi_b

    def repeated_assign():
        repeated = "first"
        repeated = "second"
        repeated

    def scoped_assign():
        scoped = False

        def fn():
            scoped = True

        # should reference the first definition of 'scoped' as the second definition
        # is scoped to only within function
        scoped

    symbol_fns = [
        (simple_fn, 0),
        (multi_assign, 0),
        (repeated_assign, 1),
        (scoped_assign, 0),
    ]

    for symbol_fn, n_def_line in symbol_fns:
        ast = parse_ast(symbol_fn)
        required_analyzers = [
            analyze_symbol,
            analyze_assign,
        ]
        for analyzer in required_analyzers:
            ast = analyzer(ast)
        analyzed_ast = resolve_symbol(ast)
        fn_ast = analyzed_ast.body[0]

        sym_def = fn_ast.body[n_def_line]
        sym_defs = sym_def.values
        sym_ref = fn_ast.body[-1].value
        sym_refs = sym_ref.elts if isinstance(sym_ref, Tuple) else [sym_ref]
        for sym_def, sym_ref in zip(sym_defs, sym_refs):
            print(sym_ref.symbol, " = ", sym_ref.definition, " => ", sym_def)
            assert sym_ref.definition == sym_def

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
    assert all(
        get_fn_ast(ast).n_args == expected_n_arg[0]
        for ast, expected_n_arg in zip(analyzed_asts, n_arg_fns)
    )

    # test docstring detection
    analyzed_ast = analyze_func(parse_ast(empty_fn_docstr))
    assert get_fn_ast(analyzed_ast).docstr is not None
    analyzed_ast = analyze_func(parse_ast(empty_fn_pass))
    assert get_fn_ast(analyzed_ast).docstr is None

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

    for ast, expected_fn in zip(analyzed_asts, convert_fns):
        fn_ast = ast.convert_fn
        assert (fn_ast is not None) == expected_fn[1]
        if fn_ast is not None:
            assert fn_ast.plotter_name == fn_ast.args.args[0].id


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
    const_asts = set(n for n in gast.walk(ast) if n.is_constant)
    assert const_asts == expected_asts


# test that qualified and unqualified symbols and be detected by symbol analyzer
def test_symbol_analyzer():
    def symbol_fn():
        x = 2
        a.b.c = "str"
        y, z = True, False
        m[k1] = "v1"
        m["k2"] = "v2"
        m["k" + "3"] = "v3"

    ast = parse_ast(symbol_fn)
    analyzed_ast = analyze_symbol(ast)
    fn_ast = analyzed_ast.body[0]
    x_target, abc_target = [fn_ast.body[i].targets[0] for i in range(2)]
    x_value, abc_value = [fn_ast.body[i].value for i in range(2)]
    assert x_target.is_symbol and x_target.symbol == "x" and x_target.base_symbol == "x"
    assert (
        abc_target.is_symbol
        and abc_target.symbol == "a.b.c"
        and abc_target.base_symbol == "a"
    )

    y_target, z_target = fn_ast.body[2].targets[0].elts
    y_value, z_value = fn_ast.body[2].value.elts
    assert y_target.is_symbol and y_target.symbol == "y" and y_target.base_symbol == "y"
    assert z_target.is_symbol and z_target.symbol == "z" and z_target.base_symbol == "z"

    mk1_target, mk2_target, mk3_target = [
        fn_ast.body[i].targets[0] for i in range(3, 6)
    ]
    mk1_value, mk2_value, mk3_value = [fn_ast.body[i].value for i in range(3, 6)]

    assert (
        mk1_target.is_symbol
        and mk1_target.symbol == "m[k1]"
        and mk1_target.base_symbol == "m"
    )
    assert (
        mk2_target.is_symbol
        and mk2_target.symbol == "m['k2']"
        and mk2_target.base_symbol == "m"
    )
    assert (
        mk3_target.is_symbol
        and mk3_target.symbol == "m[('k' + '3')]"
        and mk3_target.base_symbol == "m"
    )

    assert all(
        [
            not val.is_symbol
            for val in [x_value, abc_value, y_value, z_value, mk1_value, mk2_value]
        ]
    )


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

    def aug_assign():
        aug = 0
        aug = aug + 1
        aug

    class Qualified:
        a = 1

    def qualified_assign():
        Qualified.a = 1
        Qualified.a

    # test case functions, the line no. wrt. the function where the variable last defined
    # and finally list of all line no. where variable is defined.
    # if line no. is None, the symbols is defined global symbol
    symbol_fns = [
        (simple_fn, 0, [0]),
        (multi_assign, 0, [0]),
        (repeated_assign, 1, [0, 1]),
        (scoped_assign, 0, [0]),
        (aug_assign, 1, [0, 1]),
        (qualified_assign, 0, [0]),
    ]

    for symbol_fn, n_latest_def_line, n_def_lines in symbol_fns:
        ast = parse_ast(symbol_fn)
        required_analyzers = [
            analyze_symbol,
            analyze_assign,
        ]
        for analyzer in required_analyzers:
            ast = analyzer(ast)
        analyzed_ast = resolve_symbol(ast)
        fn_ast = analyzed_ast.body[0]

        # check latest symbol definition labeled as 'definition'
        latest_sym_def = fn_ast.body[n_latest_def_line]
        sym_ref = fn_ast.body[-1].value
        latest_sym_defs = latest_sym_def.values
        sym_refs = sym_ref.elts if isinstance(sym_ref, Tuple) else [sym_ref]
        for latest_sym_def, sym_ref in zip(latest_sym_defs, sym_refs):
            if sym_ref.definition != latest_sym_def:
                print(gast.dump(sym_ref))
                print(gast.dump(sym_ref.definition))
            assert sym_ref.definition == latest_sym_def

        # check all symbol definitions labeled as 'definitions'
        sym_defs = [fn_ast.body[n_line] for n_line in n_def_lines]
        for line_sym_defs in sym_defs:
            for sym_def, sym_ref in zip(line_sym_defs.values, sym_refs):
                if sym_ref.definitions.count(sym_def) != 1:
                    print(gast.dump(sym_ref))
                    print([gast.dump(d) for d in sym_ref.definitions])
                assert sym_ref.definitions.count(sym_def) == 1


# test that the parents of AST nodes are labeled correctly
def test_analyze_parent():
    def simple_fn():
        simple = 2

    ast = analyze_parent(parse_ast(simple_fn))
    fn_ast = ast.body[0]
    assert fn_ast.parent == ast
    assign_ast = fn_ast.body[0]
    assert assign_ast.parent == fn_ast
    simple_ast, const_ast = assign_ast.targets[0], assign_ast.value
    assert simple_ast.parent == assign_ast
    assert const_ast.parent == assign_ast


# test that code blocks can be identified and labeled correctly
def test_analyze_block():
    def ternary_fn():
        x = 1 if True else False

    def list_comp_fn():
        x = [i for i in [1, 2, 3]]

    def dict_comp_fn():
        x = {i: j for i, j in [[1, 2], [2, 3], [3, 4]]}

    def lambda_fn():
        x = lambda y: y + 2

    def func_fn():
        def fn(y):
            return y + 2

    def ifelse_fn():
        if True:
            x = 1
        else:
            x = 3

    def for_fn():
        for i in [1, 2, 3]:
            x = i
        else:
            y = i

    def while_fn():
        while True:
            x = 2

    def with_fn():
        with 1 as x:
            y = x

    def try_fn():
        try:
            x = 1
        finally:
            z = x == 1

    # test case, whether the first statement is code block, expected ast getter
    block_fns = [
        (ternary_fn, False),
        (list_comp_fn, False),
        (dict_comp_fn, False),
        (lambda_fn, False),
        (func_fn, True),
        (ifelse_fn, True),
        (for_fn, True),
        (while_fn, True),
        (with_fn, True),
        (try_fn, True),
    ]

    for fn, is_expected_block in block_fns:
        analyzed_ast = analyze_block(parse_ast(fn))
        fn_ast = analyzed_ast.body[0]
        block_ast = fn_ast.body[0]
        # check code blocks are labeled correctly
        assert block_ast.is_block == is_expected_block
        # check back edges to code block are created correctedly to child nodes
        if is_expected_block:
            for child in gast.walk(block_ast):
                # walk() will include the root block ast node..
                # ignore when checking code block back edges
                if child == block_ast:
                    continue

                if child.block != block_ast:
                    __import__("pprint").pprint((gast.dump(child.block)))
                    __import__("pprint").pprint((gast.dump(block_ast)))
                assert child.block == block_ast


def test_analyze_activity():
    def output_only_fn():
        if True:
            # since 'x' is assigned inside the if block
            # it should not be label as input_syms wrt. if block
            x = 1
            y = x + 1

    def input_only_fn():
        x, f = 1, (lambda x: x)
        if True:
            f(x)
            f(x + 3)

    def input_output_fn():
        x = 1
        if True:
            y = x + 1
            x = 2
            y = x + 3

    def nested_in_out_fn():
        x = 1
        # parent if block should obtain child node's inputs and ouputs
        if False:
            if True:
                y = x + 1
                x = 2
                y = x + 3

    def multi_in_out_fn():
        x = 0
        if True:
            x = x + 1
            y = 2
        else:
            x = x - 1
            y = 3

    class A:
        x = 1

    def qualified_in_out():
        A.x = 1
        # test with qualified symbol A.x
        if True:
            y = A.x + 1
            A.x = 2
            y = A.x + 3

    # test case, expected attributes
    activity_fns = [
        (
            output_only_fn,
            {
                "input_syms": [],
                "output_syms": ["x", "y"],
                "base_in_syms": [],
                "base_out_syms": ["x", "y"],
            },
        ),
        (
            input_only_fn,
            {
                "input_syms": ["x", "f"],
                "output_syms": [],
                "base_in_syms": ["x", "f"],
                "base_out_syms": [],
            },
        ),
        (
            input_output_fn,
            {
                "input_syms": ["x"],
                "output_syms": ["x", "y"],
                "base_in_syms": ["x"],
                "base_out_syms": ["x", "y"],
            },
        ),
        (
            nested_in_out_fn,
            {
                "input_syms": ["x"],
                "output_syms": ["x", "y"],
                "base_in_syms": ["x"],
                "base_out_syms": ["x", "y"],
            },
        ),
        (
            multi_in_out_fn,
            {
                "input_syms": ["x"],
                "output_syms": ["x", "y"],
                "base_in_syms": ["x"],
                "base_out_syms": ["x", "y"],
            },
        ),
        (
            qualified_in_out,
            {
                "input_syms": ["A.x"],
                "output_syms": ["A.x", "y"],
                "base_in_syms": ["A"],
                "base_out_syms": ["A", "y"],
            },
        ),
    ]

    for fn, expected_attrs in activity_fns:
        required_analyzers = [
            analyze_assign,
            analyze_symbol,
            resolve_symbol,
            analyze_block,
        ]
        ast = parse_ast(fn)
        for analyzer in required_analyzers:
            ast = analyzer(ast)
        analyzed_ast = analyze_activity(ast)
        fn_ast = analyzed_ast.body[0]

        # extract code block AST node
        block_ast = [n for n in gast.walk(fn_ast) if n.is_block and n != fn_ast][0]
        actual_attrs = {
            "output_syms": block_ast.output_syms.keys(),
            "input_syms": block_ast.input_syms.keys(),
            "base_in_syms": block_ast.base_in_syms.keys(),
            "base_out_syms": block_ast.base_out_syms.keys(),
        }
        # check detect of input and output symbols
        for attr in expected_attrs.keys():
            if set(actual_attrs[attr]) != set(expected_attrs[attr]):
                print(fn)
                __import__("pprint").pprint(expected_attrs)
                __import__("pprint").pprint(actual_attrs)
            assert set(actual_attrs[attr]) == set(expected_attrs[attr])

        # check contents of symbol dict
        combined_syms = list(block_ast.input_syms.items()) + list(
            block_ast.output_syms.items()
        )
        for symbol, sym_asts in combined_syms:
            assert all(ast.symbol == symbol for ast in sym_asts)
            # check sym_asts sorted by order of appearance in source code
            # (ie code pos does not decrease) https://stackoverflow.com/a/4983359
            if len(sym_asts) > 1:
                code_pos = lambda ast: (ast.lineno, ast.col_offset)
                assert all(
                    [code_pos(x) <= code_pos(y) for x, y in zip(sym_asts, sym_asts[1:])]
                )

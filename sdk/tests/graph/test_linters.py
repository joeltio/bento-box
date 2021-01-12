#
# Bentobox
# SDK - Graph
# Linters Test
#

from bento.graph.analyzers import *
from bento.graph.linters import *
from bento.graph.ast import parse_ast
from bento.graph.plotter import Plotter


def test_lint_convert_fn():
    class NotConvertFn:
        pass

    def no_args():
        pass

    def too_many_args(a, b, c=3):
        pass

    def generator_fn(g):
        yield 2

    def convert_fn(g):
        pass

    def convert_fn_type(g: Plotter):
        pass

    # define test cases: lint fn to expected error
    lint_fns = [
        (NotConvertFn, NotImplementedError),
        (no_args, TypeError),
        (too_many_args, TypeError),
        (generator_fn, ValueError),
        (convert_fn, None),
        (convert_fn_type, None),
    ]
    # required ast analyzers in order for linting to work
    req_analyzers = [
        analyze_func,
        analyze_convert_fn,
    ]

    for fn, expected_err in lint_fns:
        ast = parse_ast(fn)
        for analyze in req_analyzers:
            ast = analyze(ast)

        has_err = False
        try:
            lint_convert_fn(ast)
        except expected_err:
            has_err = True

        assert has_err if expected_err is not None else not has_err

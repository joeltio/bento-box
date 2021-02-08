#
# Bentobox
# SDK - Graph
# Transforms
#

import gast
from typing import Callable
from gast import (
    AST,
    Constant,
    Assign,
    List,
    Tuple,
    IfExp,
    If,
    Store,
    Load,
    ListComp,
    comprehension,
)
from bento.graph.plotter import Plotter
from bento.graph.ast import (
    parse_ast,
    name_ast,
    import_from_ast,
    assign_ast,
    call_func_ast,
    load_ast_module,
    wrap_func_ast,
    wrap_block_ast,
    FuncASTTransform,
)


def transform_build_graph(ast: AST) -> AST:
    """Transforms convert function to build graph function

    Requires the `analyze_convert_fn()` to analyze the AST first.
    Removes the convert function's annotations and changes the name to `build_graph`

    Args:
        ast: AST with the convert function to transform
    Returns:
        The given ast with the convert function transformed to build graph function
    """
    fn_ast = ast.convert_fn
    fn_ast.decorator_list, fn_ast.name = [], "build_graph"

    return ast


def transform_ternary(ast: AST) -> AST:
    """Transforms ternary conditional to plot Switch Nodes on computational graph.

    Requires the `analyze_convert_fn()` to analyze the AST first.
    Transforms ternary statements in the form `a if b else c` into a call to the
    Graph Plotter to plot a Switch Node `g.switch(b, a, c)` on the computation graph.

    Args:
        ast: AST to transform ternary into the plotting of a Switch Node.
    Returns:
        The given ast with ternary statements transformed into the plotting of a Switch Node.
    """

    def do_transform(ternary_ast: AST) -> AST:
        # filter out non-ternary expressions
        if not isinstance(ternary_ast, IfExp):
            return ternary_ast
        # obtain AST of calling the plotter to plotting a switch node
        plot_switch_fn = parse_ast(Plotter.switch).body[0]
        return call_func_ast(
            fn_name=plot_switch_fn.name,
            args={
                "condition": ternary_ast.test,
                "true": ternary_ast.body,
                "false": ternary_ast.orelse,
            },
            attr_parent=ast.convert_fn.plotter_name,
        )

    ternary_transform = FuncASTTransform(do_transform)

    # apply ternary transform to AST
    ast = ternary_transform.visit(ast)

    return ast


def transform_ifelse(ast: AST) -> AST:
    """Transforms if/elif/else statements to plot Switch Nodes on computational graph.

    Requires the `analyze_activity()` to analyze the AST first.
    Transforms if/elif/else statements to a functions that using the Graph Plotter
    trace the operations performed on each conditional branch.

    Collects operations for each conditional branch using the Graph plotter
    and combines them into a conditional Switch node.

        Example:
        if a:
            x = y
            z = 1
        elif b:
            x = m
            z = 2
        else:
            x = n
            z = 3

        # should be transformed into:
        def __if_block(y, m, n):
            x = y
            z = 1
            return x, z

        def __else_block(b, m, n):
            def __if_block(m, n):
                x = m
                z = 2
                return x, z

            def __else_block(m, n):
                x = n
                z = 2
                return x, z

            from copy import deepcopy
            __if_condition = deepcopy(b)
            __if_outputs = if_block(m=deepcopy(m), n=deepcopy(n))
            __else_outputs = else_block(m=deepcopy(m), n=deepcopy(n))

            x, z = [g.switch(__if_condition, if_out, else_out) for if_out, else_out in zip(__if_outputs, __else_outputs)]
            return x, z

        from copy import deepcopy
        __if_condition = deepcopy(a)
        __if_outputs = __if_block(b=deepcopy(b), m=deepcopy(m), n=deepcopy(n))
        __else_outputs = __else_block(b=deepcopy(n), m=deepcopy(m), n=deepcopy(n))

        x, z = [g.switch(__if_condition, if_out, else_out) for if_out, else_out in zip(__if_outputs, __else_outputs)]

        # which will evaluate to:
        x = g.switch(a, y, g.switch(b, m, n))
        z = g.switch(a, 1, g.switch(b, 2, 3))

    Note:
        Defining a symbol inside the if statement requires that means that
        that symbol has be defined in all conditional branches.

        Since all branches of the if statement are traced, symbols used in the
        if statement must be `deepcopy()`able. `deepcopy()` is used to ensure
        that variables in different branches don't interfere with each other.

    Args:
        ast: AST to transform if else statements into the plotting of a Switch Node.
    Returns:
        The given ast with if else statements to be transformed into a the plotting of a Switch Node.
    """

    def do_transform(ifelse_ast: AST) -> AST:
        # filter out non-ifelse statements
        if not isinstance(ifelse_ast, If):
            return ifelse_ast

        # convert ifelse condition branches into functions with the arguments
        # set to the names of the base input symbols and return values set to output symbols.
        # base symbols are use to generate the arguments as the full symbol might be qualified
        # ie A.x which is not a valid argument name: https://github.com/joeltio/bento-box/issues/37
        args = list(ifelse_ast.base_in_syms.keys())
        returns = list(ifelse_ast.output_syms.keys())
        fn_asts = [
            wrap_func_ast(
                name=name,
                args=args,
                block=block,
                returns=returns,
                # zip() requires the returned outputs to be iterable
                return_tuple=True,
            )
            for name, block in zip(
                ["__if_block", "__else_block"], [ifelse_ast.body, ifelse_ast.orelse]
            )
        ]

        # deepcopy the condition before tracing the if/else block functions to
        # prevent side effects tracing from interfering with the condition.
        condition_ast = name_ast("__if_condition")
        eval_condition_ast = assign_ast(
            targets=[condition_ast],
            values=[call_func_ast("deepcopy", args=[ifelse_ast.test])],
        )

        # call if/else block functions to trace results of evaluating each branch
        # of the conditional if/else block functions have arguments with the same
        # names as symbols we have to pass in.
        # deepcopy to prevent input symbols from being passed by reference and
        # causing interference between branches https://github.com/joeltio/bento-box/issues/39
        import_deepcopy_ast = import_from_ast(module="copy", names=["deepcopy"])

        call_args = {
            a: call_func_ast(
                fn_name="deepcopy",
                args=[name_ast(a)],
            )
            for a in args
        }
        branch_outputs = [name_ast(n) for n in ["__if_outputs", "__else_outputs"]]
        call_fn_asts = [
            assign_ast(
                targets=[target],
                values=[call_func_ast(fn_ast.name, args=call_args)],
            )
            for target, fn_ast in zip(branch_outputs, fn_asts)
        ]

        # create switch nodes for each output symbol via list comprehension
        plot_switch_fn = parse_ast(Plotter.switch).body[0]
        # g.switch(test, if_out, else_out)
        call_switch_ast = call_func_ast(
            fn_name=plot_switch_fn.name,
            args={
                "condition": condition_ast,
                "true": name_ast("if_out"),
                "false": name_ast("else_out"),
            },
            attr_parent=ast.convert_fn.plotter_name,
        )

        # (symbol, ...) = [g.switch(...) for if_out, else_out in zip(if_outputs, else_outputs)]
        switch_asts = assign_ast(
            targets=[name_ast(r, ctx=Store()) for r in returns],
            values=[
                ListComp(
                    elt=call_switch_ast,
                    generators=[
                        comprehension(
                            target=Tuple(
                                elts=[
                                    name_ast("if_out"),
                                    name_ast("else_out"),
                                ],
                                ctx=Load(),
                            ),
                            iter=call_func_ast(
                                fn_name="zip",
                                args=branch_outputs,
                            ),
                            ifs=[],
                            is_async=False,
                        )
                    ],
                )
            ],
            force_tuple=True,
        )
        # wrap transformed code block as single AST node
        return wrap_block_ast(
            block=fn_asts
            + [import_deepcopy_ast, eval_condition_ast]
            + call_fn_asts
            + [switch_asts],
        )

    ifelse_transform = FuncASTTransform(do_transform)

    # apply ifelse transform to AST
    ast = ifelse_transform.visit(ast)
    mod = load_ast_module(ast)

    return ast

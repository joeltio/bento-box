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
    Transforms if/elif/else statements to a function that evaluates to calls to
    the Graph Plotter to plot a Switch Node on the computational graph.

    Note:
        Defining a symbol inside the if statement requires that means that
        that symbol has be defined in all conditional branches.

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

             __if_outputs = if_block(m)
             __else_outputs = else_block(m, n)

             x, z = [g.switch(b, if_out, else_out) for if_out, else_out in zip(__if_outputs, __else_outputs)]
             return x, z

         __if_outputs = __if_block(y)
         __else_outputs = __else_block(b, m, n)

         x, z = [g.switch(b, if_out, else_out) for if_out, else_out in zip(__if_outputs, __else_outputs)]

         # which will evaluate to:
         x = g.switch(a, y, g.switch(b, m, n))
         z = g.switch(a, 1, g.switch(b, 2, 3))

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
        # set to the names of the input symbols and return values set to output symbols
        args = list(ifelse_ast.input_syms.keys())
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
        # call if/else block functions to trace results of evaluating each branch of the conditional
        # if/else block functions have arguments with the same names as symbols we have to pass in.
        call_args = {a: name_ast(a) for a in args}
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
                "condition": ifelse_ast.test,
                "true": name_ast("if_out"),
                "false": name_ast("else_out"),
            },
            attr_parent=ast.convert_fn.plotter_name,
        )

        # symbols = [g.switch(...) for if_out, else_out in zip(if_outputs, else_outputs)]
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
        )
        # wrap transformed code block as single AST node
        return wrap_block_ast(
            block=fn_asts + call_fn_asts + [switch_asts],
        )

    ifelse_transform = FuncASTTransform(do_transform)

    # apply ifelse transform to AST
    ast = ifelse_transform.visit(ast)
    mod = load_ast_module(ast)

    return ast

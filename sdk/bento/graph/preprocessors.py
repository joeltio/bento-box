#
# Bentobox
# SDK - Graph
# Preprocessors
#

import ast
from copy import deepcopy
from typing import Callable
from gast import AST, Assign, AugAssign, BinOp, Load, Store
from bento.graph.plotter import Plotter
from bento.graph.ast import parse_ast, call_func_ast, FuncASTTransform


def preprocess_augassign(ast: AST) -> AST:
    """Preprocesses AugAssign into seperate assignment and binary operation AST node

    Preprocesses by transforming the `AugAssign` AST node into seperate `Assign` AST
    and binary operation AST nodes.

    Example:
        x += y => x = x + y

    Args:
        ast: AST with the AugAssign AST nodes to preprocess.
    Returns:
        The given ast with the AugAssign AST nodes preprocessed into separate
        Assign and operation nodes.
    """

    def do_preprocess(ast: AST) -> AST:
        # filter out non AugAssign AST nodes
        if not isinstance(ast, AugAssign):
            return ast
        aug = ast
        # the aug assign target is both loaded from and stored to.
        target_store, target_load = deepcopy(aug.target), deepcopy(aug.target)
        target_load.ctx = Load()
        target_store.ctx = Store()
        # transform AugAssign into Assign and BinOp
        bin_op = BinOp(left=target_load, op=aug.op, right=aug.value)
        return Assign(targets=[target_store], value=bin_op)

    preprocess = FuncASTTransform(do_preprocess)
    ast = preprocess.visit(ast)

    return ast

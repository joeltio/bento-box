#
# Bentobox
# SDK - Graph
# Linters
#

import gast
from gast import AST, FunctionDef


def lint_convert_fn(ast: AST):
    """Check the target convert function to ensure it is valid for conversion

    Ensures that the target convert function actually present
    Performs the following static checks on the target convert `FunctionDef`:
    - Check that it has one argument: the graph Plotter.
    - Does not produce a generator ie no `yield` statements

    Args:
        ast:
            AST to lint target convert function in.

    Raises:
        NotImplementedError: If target function could not be found.
        TypeError: If target function does not have the correct number of arguments
        ValueError: If the target function is a generator (ie has yield statements).
    """
    if ast.convert_fn is None:
        raise NotImplementedError("Missing convert function to convert to graph")
    if ast.convert_fn.n_args != 1:
        raise TypeError("Expected convert function to only have one Plotter argument")
    if ast.convert_fn.is_generator:
        raise ValueError(
            "Cannot convert a generator function. Convert function contains a yield statement."
        )

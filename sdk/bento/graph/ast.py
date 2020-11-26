#
# Bentobox
# SDK - Graph
# AST Utils
#


import gast

from gast import AST
from inspect import getsource, cleandoc
from textwrap import dedent
from typing import Any


def parse_ast(obj: Any) -> AST:
    """Parse the AST of the given `obj`.

    Args:
        obj: Object to obtain AST for. Can be any object supported by `inspect.getsource()`.

    Returns:
        The AST parsed from the the given `obj`
    """
    src = getsource(obj)
    clean_src = dedent((src))
    return gast.parse(clean_src)

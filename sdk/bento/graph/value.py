#
# Bentobox
# SDK - Graph
# Graph Value
#

from typing import Any
from bento.value import wrap
from bento.protos.graph_pb2 import Node


def wrap_const(val: Any):
    """Wrap the given native value as a Constant graph node.
    If val is a Constant node, returns value as is.
    Args:
        val: Native value to wrap.
    Returns:
        The given value wrapped as a constant graph node.
    """
    # check if already constant node, return as is if true.
    if isinstance(val, Node) and val.WhichOneof("op") == "const_op":
        return val
    return Node(const_op=Node.Const(held_value=wrap(val)))

#
# Bentobox
# SDK - Value
#

# type ignore required here as numpy does not have type stubs yet
import numpy as np  # type: ignore
from typing import Any
from inspect import isgenerator
from bento import types
from bento.protos.values_pb2 import Value
from bento.protos.types_pb2 import Type


# Native to Protobuf Value conversion
def wrap_primitive(val: Any) -> Value:
    """Wraps the given primitive native value `val` as Protobuf `Value` message.

    Args:
        val: The native value to wrap as a protobuf message.
    Returns:
        Wrapped `Value` protobuf message.
    Throws:
        TypeError: If the given native value is not of a supported primitive type.
    """
    # check if int value is 32 bit via fit within max 32 bit int value
    is_int32 = lambda x: -(2 ** 31) <= x < 2 ** 31
    if type(val) in [int, np.int32] and is_int32(val):
        return Value(
            data_type=types.int32,
            primitive=Value.Primitive(int_32=int(val)),
        )
    elif type(val) in [int, np.int64]:
        return Value(
            data_type=types.int64,
            primitive=Value.Primitive(int_64=int(val)),
        )
    # TODO(mrzzy): figure out how to check if value fits within 32 bits
    elif type(val) in [float, np.float64]:
        return Value(
            data_type=types.float64,
            primitive=Value.Primitive(float_64=float(val)),
        )
    elif type(val) in [str, np.str_]:
        return Value(
            data_type=types.string,
            primitive=Value.Primitive(str_val=str(val)),
        )
    elif type(val) in [bool, np.bool_]:
        return Value(
            data_type=types.boolean,
            primitive=Value.Primitive(boolean=bool(val)),
        )
    else:
        raise TypeError(
            f"{type(val)} is not a supported native primitive type to wrap as Value proto."
        )


def wrap(val: Any) -> Value:
    """Wraps the given native `val` as Protobuf `Value` message.

    Supports converting collection/array of primitives types to `Value` message:
    * numpy array of primitives.
    * list of primitives.
    * generator of finite no. of primitives.

    Generally, wrapping only supports wrapping of collection of primitives
    if all primitives share the same native primitive types. However, some
    native type mixing is allowed as supported by `np.asarray()`, although
    doing so is not recommended.

    If the given `val` is already a Protobuf `Value` message, returns `val` as is.

    Args:
        val: The native value to wrap as a protobuf message. The value should
            be native primitive, array of primitives.
    Returns:
        Wrapped `Value` protobuf message.
    Throws:
        TypeError: If the given native value is not of a supported type.
    """
    # return as is if val is already value protobuf
    if isinstance(val, Value):
        return val
    # try to wrap value as primitive
    try:
        return wrap_primitive(val)
    except TypeError:
        pass
    # check that we are not trying to convert None
    if val is None:
        raise TypeError("Wrapping None is Value proto is not supported")
    # extract values from if generator
    if isgenerator(val):
        val = list(val)
    # extract flatten list of primitive protos from collect of primitives
    val_arr = np.asarray(val)
    primitives = [wrap_primitive(v) for v in val_arr.flatten()]
    # resolve element data type and build value proto
    element_type = primitives[0].data_type.primitive
    return Value(
        data_type=Type(
            array=Type.Array(
                dimensions=val_arr.shape,
                element_type=element_type,
            )
        ),
        array=Value.Array(values=[p.primitive for p in primitives]),
    )


def unwrap_primitive(value: Value) -> Any:
    """Unwrap the given Value proto into its native primitive value equivalent.
    Args:
        value: The Value proto to unwrap into native value.
    Returns:
        The unwrapped native value drived from the Value proto.
    Raises:
        TypeError: When given a Value does not contain a primitive.
        ValueError: When given a invalid Value proto to unwrap.
    """
    dtype = value.data_type
    if not dtype.WhichOneof("kind") == "primitive":
        raise TypeError("Only supports unwraping Value containing primitives")
    if dtype.primitive == Type.Primitive.BYTE:
        return value.primitive.int_8
    elif dtype.primitive == Type.Primitive.INT32:
        return value.primitive.int_32
    elif dtype.primitive == Type.Primitive.INT64:
        return value.primitive.int_64
    elif dtype.primitive == Type.Primitive.FLOAT32:
        return value.primitive.float_32
    elif dtype.primitive == Type.Primitive.FLOAT64:
        return value.primitive.float_64
    elif dtype.primitive == Type.Primitive.BOOL:
        return value.primitive.boolean
    elif dtype.primitive == Type.Primitive.STRING:
        return value.primitive.str_val
    elif dtype.primitive == Type.Primitive.INVALID:
        raise ValueError("Unable to unwrap Value with INVALID Type")


def unwrap(value: Value) -> Any:
    """Unwrap the given Value proto into its native value equivalent.
    Args:
        value: The Value proto to unwrap into native value.
    Returns:
        The unwrapped native value drived from the Value proto.
    Raises:
        TypeError: When given a Value does not contain supported data type kind.
        ValueError: When given a invalid Value proto to unwrap.
    """
    dtype = value.data_type
    dtype_kind = dtype.WhichOneof("kind")
    if dtype_kind == "primitive":
        return unwrap_primitive(value)
    elif dtype_kind != "array":
        raise TypeError(f"Unable to unwrap unsupported data type kind: {dtype_kind}")
    # extract primitive Values form Value protos
    primitive_values = [
        Value(
            primitive=v,
            data_type=Type(primitive=dtype.array.element_type),
        )
        for v in value.array.values
    ]
    # construct np array with native values and shape
    native_vals = [unwrap_primitive(v) for v in primitive_values]
    return np.asarray(native_vals).reshape(dtype.array.dimensions)

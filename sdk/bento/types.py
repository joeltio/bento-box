#
# Bentobox
# SDK - Types
#
"""
Provides access to primitive data types supported by `bentobox-sdk`
"""


from bento.protos.types_pb2 import Type

# Provide easier access to Proto types
byte = Type(primitive=Type.Primitive.BYTE)
int32 = Type(primitive=Type.Primitive.INT32)
int64 = Type(primitive=Type.Primitive.INT64)
float32 = Type(primitive=Type.Primitive.FLOAT32)
float64 = Type(primitive=Type.Primitive.FLOAT64)
boolean = Type(primitive=Type.Primitive.BOOL)
string = Type(primitive=Type.Primitive.STRING)

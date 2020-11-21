#
# Bentobox
# SDK
# SDK Unit tests
#

from bento.protos.references_pb2 import AttributeRef

# Tests if we can build protobuf messages
def test_build_proto():
    attr_ref = AttributeRef(
        entity_id=24,
        component="Sprite2D",
    )
    encoded = attr_ref.SerializeToString()
    restored = AttributeRef()
    restored.ParseFromString(encoded)
    assert attr_ref == restored

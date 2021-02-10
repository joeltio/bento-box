#
# Bentobox
# SDK
# Utilities
#

from bento.protos.references_pb2 import AttributeRef
from google.protobuf.json_format import MessageToDict, MessageToJson
from google.protobuf.message import Message
import yaml


def to_yaml_proto(proto: Message):
    """Convert and return the given protobuf message as YAML"""
    return yaml.safe_dump(MessageToDict(proto), sort_keys=True)


def to_str_attr(attr: AttributeRef):
    return f"{attr.entity_id}/{attr.component}/{attr.attribute}"

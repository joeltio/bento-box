#
# Bentobox
# SDK
# Utilities
#

import yaml
from google.protobuf.message import Message
from google.protobuf.json_format import MessageToDict, MessageToJson


def to_yaml_proto(proto: Message):
    """Convert and return the given protobuf message as YAML"""
    return yaml.safe_dump(MessageToDict(proto), sort_keys=True)

#
# Bentobox
# SDK
# Utilities
#

import yaml
import json
from difflib import unified_diff, ndiff
from google.protobuf.json_format import MessageToDict, MessageToJson


def to_yaml_proto(proto):
    """Convert and return the given protobuf message as YAML"""
    return yaml.safe_dump(json.loads(MessageToJson(proto, sort_keys=True)))

#
# Bentobox
# SDK - Tests
# Testing utilities
#

from google.protobuf.json_format import MessageToJson


def assert_proto(actual_proto, expected_proto):
    """Assert that actual_proto is equal to expected_proto.

    Disregards the order of repeated fields, as long as they have the same elements,
    they are condsidered equal.
    """
    # pytest -vv gives us a nice diff when comparing as JSON
    assert MessageToJson(actual_proto, sort_keys=True) == MessageToJson(
        expected_proto, sort_keys=True
    )

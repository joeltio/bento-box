#
# Bentobox
# SDK - ECS
# gRPC based ECS Tests
#

import pytest
from unittest.mock import Mock

from bento import types
from bento.value import wrap
from bento.client import Client
from bento.ecs.spec import ComponentDef
from bento.ecs.grpc import Component, Entity
from bento.protos.references_pb2 import AttributeRef


@pytest.fixture
def mock_client():
    mock_client = Mock(spec=Client)
    mock_client.get_attr.return_value = wrap(3.2)
    return mock_client


@pytest.fixture
def component(mock_client):
    # test grpc component
    return Component(entity_id=1, name="position", client=mock_client)


def test_ecs_grpc_component_get_attr(component):
    val = component.get_attr("x")
    assert val == 3.2
    # test __getattr__ syntax
    val = component.x
    assert val == 3.2


def test_ecs_grpc_component_get_attr(component, mock_client):
    def check_client_set_attr(x):
        mock_client.set_attr.assert_called_with(
            attr_ref=AttributeRef(entity_id=1, component="position", attribute="y"),
            value=wrap(x),
        )

    component.set_attr("y", 15)
    check_client_set_attr(15)

    # test __setattr__ syntax
    component.y = 12
    check_client_set_attr(12)


@pytest.fixture
def entity(mock_client):
    # test grpc entity
    return Entity(components=["position"], entity_id=1, client=mock_client)


def test_ecs_grpc_entity_get_component(entity, mock_client):
    def check_component(component):
        assert (
            component._entity_id == 1
            and component._name == "position"
            and component._client == mock_client
        )

    component = entity.get_component("position")
    check_component(component)
    # test __getitem__ syntax
    component = entity["position"]
    check_component(component)

    # test __getitem__ with ComponentDef syntax
    Position = ComponentDef(
        name="position",
        schema={
            "x": types.float32,
        },
    )
    component = entity[Position]
    check_component(component)

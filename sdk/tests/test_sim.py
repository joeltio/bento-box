#
# Bentobox
# SDK - Simulation
# Simulation
#

import pytest
from unittest.mock import Mock

from bento import types
from bento.client import Client
from bento.sim import Simulation
from bento.ecs.spec import EntityDef, ComponentDef, SystemDef
from bento.protos.sim_pb2 import SimulationDef
from tests.utils import assert_proto


@pytest.fixture
def component_defs():
    return [
        ComponentDef(
            name="position",
            schema={
                "x": types.int32,
                "y": types.int32,
            },
        ),
        ComponentDef(
            name="health",
            schema={
                "current": types.int32,
                "max": types.int32,
            },
        ),
    ]


@pytest.fixture
def entity_defs(component_defs):
    return [EntityDef(entity_id=1, components=component_defs)]


@pytest.fixture
def sim_proto(component_defs, entity_defs):
    return SimulationDef(
        name="test_sim",
        entities=[e.proto for e in entity_defs],
        components=[c.proto for c in component_defs],
    )


@pytest.fixture
def mock_client(sim_proto):
    client = Mock(spec=Client)
    client.apply_sim.return_value = sim_proto
    return client


@pytest.fixture
def sim(mock_client, component_defs, entity_defs):
    """Simulation object for testing"""
    return Simulation(
        name="test_sim",
        components=component_defs,
        entities=entity_defs,
        client=mock_client,
    )


def test_sim_simulation_start(sim, mock_client, sim_proto):
    sim.start()
    mock_client.apply_sim.assert_called_once()
    actual_sim_proto = mock_client.apply_sim.call_args[0][0]
    assert_proto(actual_sim_proto, sim_proto)


def test_sim_simulation_end(sim, mock_client):
    sim.started = True
    sim.stop()
    mock_client.remove_sim.assert_called_once_with(sim.name)


def test_sim_simulation_with(sim):
    # test that exceptions are not suppress by with statement
    has_error = False
    try:
        with sim:
            raise RuntimeError("Test Error")
    except RuntimeError:
        has_error = True
    assert has_error


def test_sim_simulation_entity(sim, entity_defs, component_defs):
    sim.start()
    entity = sim.entity([c.name for c in component_defs])
    assert entity.entity_id == 1

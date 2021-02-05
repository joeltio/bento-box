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
from bento.utils import to_yaml_proto
from bento.graph.plotter import Plotter
from bento.ecs.spec import EntityDef, ComponentDef, SystemDef
from bento.example.specs import Position, Speed
from bento.protos.sim_pb2 import SimulationDef


@pytest.fixture
def component_defs():
    return [Position, Speed]


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


def test_sim_simulation_init(mock_client, component_defs, entity_defs, sim_proto):
    # remove ids from entity_def to simulate entity defs created by use without entity_id set.
    noid_entity_defs = []
    for entity_def in entity_defs:
        entity_def.proto.id = 0
        noid_entity_defs.append(entity_def)

    noid_sim_proto = SimulationDef()
    noid_sim_proto.CopyFrom(sim_proto)
    del noid_sim_proto.entities[:]
    noid_sim_proto.entities.extend([e.proto for e in noid_entity_defs])

    sim = Simulation(
        name="test_sim",
        components=component_defs,
        entities=noid_entity_defs,
        client=mock_client,
    )

    # check for apply to obtain entity ids
    mock_client.apply_sim.assert_called_once()
    actual_sim_proto = mock_client.apply_sim.call_args[0][0]
    assert to_yaml_proto(actual_sim_proto) == to_yaml_proto(noid_sim_proto)

    # check entity ids provided by the engine are applied
    assert sim.entities[0].id == 1


def test_sim_simulation_start(sim, mock_client, sim_proto):
    sim.start()
    assert sim.started
    # test calling again does nothing
    sim.start()
    assert sim.started


def test_sim_simulation_end(sim, mock_client):
    # test for RuntimeError when stepping a sim that has not started
    has_error = False
    try:
        sim.stop()
    except RuntimeError:
        has_error = True
    assert has_error

    sim.start()
    sim.stop()
    mock_client.remove_sim.assert_called_once_with(sim.name)


def test_sim_simulation_step(sim, mock_client):
    # test for RuntimeError when stepping a sim that has not started
    has_error = False
    try:
        sim.step()
    except RuntimeError:
        has_error = True
    assert has_error

    sim.start()
    sim.step()
    mock_client.step_sim.assert_called_once_with(sim.name)

    # test for RuntimeError when stepping a sim that has already stopped
    sim.stop()
    has_error = False
    try:
        sim.step()
    except RuntimeError:
        has_error = True
    assert has_error


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
    component_names = [c.name for c in component_defs]
    entity = sim.entity(component_names)
    assert entity.entity_id == 1
    assert frozenset([c.component_name for c in entity.components]) == frozenset(
        component_names
    )


def test_sim_simulation_system(sim, entity_defs, component_defs):
    @sim.system
    def test_sim_fn(g: Plotter):
        # test that we can use registered entiies and components when plotting
        car = g.entity(components=[Position, Speed])
        car[Position].x = 2 * car[Speed].x_neg

    # check system is added
    assert len(sim.system_defs) == 1

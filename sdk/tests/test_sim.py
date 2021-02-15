#
# Bentobox
# SDK - Simulation
# Simulation
#

from unittest.mock import Mock

import pytest
from bento import types
from bento.client import Client
from bento.example.specs import Position, Speed
from bento.graph.compile import compile_graph
from bento.graph.plotter import Plotter
from bento.protos import sim_pb2
from bento.sim import Simulation
from bento.spec.ecs import ComponentDef, EntityDef, SystemDef
from bento.spec.graph import Graph
from bento.spec.sim import SimulationDef
from bento.utils import to_yaml_proto


# test init graph & system
def init_fn(g: Plotter):
    car = g.entity(components=[Position, Speed])
    car[Position].x = 50
    car[Position].y = 25
    car[Speed].x = 1
    car[Speed].y = 2


def sys_fn(g: Plotter):
    car = g.entity(components=[Position, Speed])
    car[Position].x = 2 * car[Speed].x_neg


@pytest.fixture
def component_defs():
    return [Position, Speed]


@pytest.fixture
def entity_defs(component_defs):
    return [EntityDef(entity_id=1, components=component_defs)]


@pytest.fixture
def system_defs(component_defs, entity_defs):
    return [
        SystemDef(graph=compile_graph(sys_fn, entity_defs, component_defs), system_id=1)
    ]


@pytest.fixture
def init_graph(component_defs, entity_defs):
    return compile_graph(init_fn, entity_defs, component_defs)


@pytest.fixture
def sim_proto(component_defs, entity_defs, system_defs, init_graph):
    return sim_pb2.SimulationDef(
        name="test_sim",
        entities=[e.proto for e in entity_defs],
        components=[c.proto for c in component_defs],
        systems=[s.proto for s in system_defs],
        init_graph=init_graph.proto,
    )


@pytest.fixture
def init_sim_proto(component_defs, entity_defs, sim_proto):
    # remove ids from entity_def to simulate entity defs created by use without entity_id set.
    init_entity_defs = []
    for entity_def in entity_defs:
        entity_def.proto.id = 0
        init_entity_defs.append(entity_def)

    init_sim_proto = sim_pb2.SimulationDef()
    init_sim_proto.CopyFrom(sim_proto)
    del init_sim_proto.entities[:]
    init_sim_proto.entities.extend([e.proto for e in init_entity_defs])

    # remove init graph and systems as those are not applied on first apply_sim call
    init_sim_proto.init_graph.Clear()
    del init_sim_proto.systems[:]

    return init_sim_proto


@pytest.fixture
def mock_client():
    client = Mock(spec=Client)
    return client


@pytest.fixture
def sim(mock_client, component_defs, entity_defs, sim_proto):
    """Simulation object for testing"""
    mock_client.apply_sim.return_value = sim_proto

    return Simulation(
        name="test_sim",
        components=component_defs,
        entities=entity_defs,
        system_fns=[sys_fn],
        init_fn=init_fn,
        client=mock_client,
    )


@pytest.fixture
def sim_def(component_defs, entity_defs, system_defs):
    return SimulationDef(
        name="test_sim",
        components=component_defs,
        entities=entity_defs,
        system_fns=[sys_fn],
        init_fn=init_fn,
    )


def test_simulation_create(
    mock_client,
    component_defs,
    entity_defs,
    system_defs,
    sim_proto,
    init_sim_proto,
):
    noid_entity_defs = []
    for entity_def in entity_defs:
        entity_def.proto.id = 0
        noid_entity_defs.append(entity_def)

    mock_client.apply_sim.return_value = sim_proto
    sim = Simulation(
        name="test_sim",
        components=component_defs,
        entities=noid_entity_defs,
        system_fns=[sys_fn],
        init_fn=init_fn,
        client=mock_client,
    )

    # check for init apply to obtain entity ids
    mock_client.apply_sim.assert_called_once()
    actual_sim_proto = mock_client.apply_sim.call_args[0][0]
    assert to_yaml_proto(actual_sim_proto) == to_yaml_proto(init_sim_proto)

    # check entity ids provided by the engine are applied
    assert sim.entities[0].id == 1


def test_simulation_from_def(mock_client, sim_def, sim_proto, init_sim_proto):
    mock_client.apply_sim.return_value = sim_proto
    sim = Simulation.from_def(sim_def, mock_client)

    # check for init apply to obtain entity ids
    mock_client.apply_sim.assert_called_once()
    actual_sim_proto = mock_client.apply_sim.call_args[0][0]
    assert to_yaml_proto(actual_sim_proto) == to_yaml_proto(init_sim_proto)


def test_simulation_start(sim, mock_client, sim_proto):
    sim.start()
    assert sim.started
    # check that system ids are set
    system_ids = frozenset(system_id for _, system_id in sim.system_fns)
    assert 0 not in system_ids
    # test calling again does nothing
    sim.start()
    assert sim.started


def test_simulation_end(sim, mock_client):
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


def test_simulation_step(sim, mock_client):
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


def test_simulation_with(sim):
    # test that exceptions are not suppress by with statement
    has_error = False
    try:
        with sim:
            raise RuntimeError("Test Error")
    except RuntimeError:
        has_error = True
    assert has_error


def test_simulation_entity(sim, entity_defs, component_defs):
    sim.start()
    entity = sim.entity([Position, Speed])
    assert entity.entity_id == 1

    assert frozenset([c.component_name for c in entity.components]) == frozenset(
        [c.name for c in component_defs]
    )


def test_simulation_system(sim, entity_defs, component_defs, system_defs):
    sim.system(sys_fn)
    expected_graph = system_defs[0].graph
    built_proto = sim.build()
    assert len(built_proto.systems) == 2
    assert Graph.from_proto(built_proto.systems[-1].graph).yaml == expected_graph.yaml


def test_simulation_init_graph(sim, entity_defs, component_defs, init_graph):
    sim.init(init_fn)
    assert Graph.from_proto(sim.build().init_graph).yaml == init_graph.yaml

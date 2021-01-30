#
# Bentobox
# SDK - Graph Tests
# Test graph compilation
#

import yaml
import pytest
from os import path
from unittest.mock import Mock
from typing import Callable, Any
from google.protobuf.json_format import MessageToDict, ParseDict, MessageToJson

from bento.client import Client
from bento.sim import Simulation
from tests.utils import assert_proto
from bento.graph.plotter import Plotter
from bento.graph.value import wrap_const
from bento.graph.compile import compile_graph
from bento.protos.graph_pb2 import Graph, Node
from bento.protos.sim_pb2 import SimulationDef
from bento.protos.references_pb2 import AttributeRef
from bento.ecs.spec import EntityDef, ComponentDef
from tests.components import Position, Speed, Clock

## test tools
# path to graph test cases in test resources
GRAPH_DIR = path.join(path.dirname(__file__), "resources")


def sort_input_outputs(graph: Graph):
    inputs = sorted(graph.inputs, key=(lambda n: str(n.retrieve_attr)))
    del graph.inputs[:]
    graph.inputs.extend(inputs)

    outputs = sorted(graph.outputs, key=(lambda n: str(n.mutate_attr)))
    del graph.outputs[:]
    graph.outputs.extend(outputs)
    return graph


def assert_graph(actual: Graph, expected_path: str):
    with open(path.join(GRAPH_DIR, expected_path), "r") as f:
        expected = Graph()
        ParseDict(yaml.safe_load(f.read()), expected)
    # sort graph inputs and outputs to ensure position invariance when comparing
    actual, expected = sort_input_outputs(actual), sort_input_outputs(expected)
    # pytest -vv gives us a nice diff when comparing as JSON
    assert_proto(actual, expected)


def build_sim(component_defs, entity_defs):
    mock_client = Mock(spec=Client)
    mock_client.apply_sim.return_value = SimulationDef(
        name="test_sim",
        entities=[e.proto for e in entity_defs],
        components=[c.proto for c in component_defs],
    )
    sim = Simulation(
        name="test_sim",
        entities=entity_defs,
        components=component_defs,
        client=mock_client,
    )
    sim.start()
    return sim


## tests
# test that empty no op functions are compilable
def test_graph_compile_empty():
    sim = build_sim(component_defs=[], entity_defs=[])

    @compile_graph(sim)
    def actual_graph(g: Plotter):
        pass

    assert actual_graph == Graph()


# test compile basic arithmetic example with one entity
def test_graph_compile_arithmetic():
    sim = build_sim(
        component_defs=[Position],
        entity_defs=[EntityDef(components=[Position], entity_id=1)],
    )
    print(sim.entity_map)

    @compile_graph(sim)
    def actual_graph(g: Plotter):
        car = g.entity(components=["position"])
        x_delta = 20
        car["position"].x += x_delta

    assert_graph(actual_graph, "expected_graph_arithmetic.yaml")


# test compile basic arithmetic example with multiple entities
def test_graph_compile_arithmetic_multiple():
    sim = build_sim(
        component_defs=[Position, Speed, Clock],
        entity_defs=[
            EntityDef(components=[Position, Speed], entity_id=1),
            EntityDef(components=[Clock], entity_id=2),
        ],
    )

    @compile_graph(sim)
    def actual_graph(g: Plotter):
        ms_in_sec = int(1e3)
        env = g.entity(components=["clock"])
        car = g.entity(
            components=[
                "position",
                "speed",
            ]
        )
        tick_ms = env["clock"].tick_ms
        xps = -car["speed"].x_neg
        x_delta = xps * (tick_ms * ms_in_sec)
        car["position"].x = x_delta + car["position"].x

    assert_graph(actual_graph, "expected_graph_arithmetic_multiple.yaml")


# test compile ternary conditional
def test_graph_compile_ternary():
    sim = build_sim(
        component_defs=[Position, Clock],
        entity_defs=[
            EntityDef(components=[Position], entity_id=1),
            EntityDef(components=[Clock], entity_id=2),
        ],
    )

    @compile_graph(sim)
    def actual_graph(g: Plotter):
        car = g.entity(
            components=[
                "position",
            ]
        )
        env = g.entity(components=["clock"])
        x_delta = 20 if env["clock"].tick_ms > 2000 else 10
        car["position"].x = x_delta

    assert_graph(actual_graph, "expected_graph_ternary.yaml")


# test compil if else conditional conditional
def test_graph_compile_ifelse():
    sim = build_sim(
        component_defs=[Position, Clock],
        entity_defs=[
            EntityDef(components=[Position], entity_id=1),
            EntityDef(components=[Clock], entity_id=2),
        ],
    )

    @compile_graph(sim)
    def actual_graph(g: Plotter):
        car = g.entity(
            components=[
                "position",
            ]
        )
        env = g.entity(components=["clock"])
        if env["clock"].tick_ms > 2000:
            x_delta = 20
            y_delta = x_delta + 2
        elif env["clock"].tick_ms > 5000:
            x_delta = 50
            y_delta = x_delta + 10
        else:
            x_delta = 10
            y_delta = x_delta - 5
        car["position"].x += x_delta
        car["position"].y += y_delta

    assert_graph(actual_graph, "expected_graph_ifelse.yaml")

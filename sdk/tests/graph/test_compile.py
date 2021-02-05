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
from bento.utils import to_yaml_proto
from bento.graph.plotter import Plotter
from bento.graph.value import wrap_const
from bento.graph.compile import compile_graph
from bento.protos.graph_pb2 import Graph, Node
from bento.protos.sim_pb2 import SimulationDef
from bento.protos.references_pb2 import AttributeRef
from bento.ecs.spec import EntityDef, ComponentDef
from bento.example.specs import Position, Speed, Clock, Velocity

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
    # pytest -vv gives us a nice diff when comparing as YAML
    assert to_yaml_proto(actual) == to_yaml_proto(expected)


## tests
# test that empty no op functions are compilable
def test_graph_compile_empty():
    def empty_fn(g: Plotter):
        pass

    actual_graph = compile_graph(
        convert_fn=empty_fn,
        entity_defs=[],
        component_defs=[],
    )
    assert actual_graph == Graph()


# test compile basic arithmetic example with one entity
def test_graph_compile_arithmetic():
    def arithmetic_fn(g: Plotter):
        car = g.entity(components=[Position])
        x_delta = 20
        car[Position].x += x_delta

    actual_graph = compile_graph(
        convert_fn=arithmetic_fn,
        component_defs=[Position],
        entity_defs=[EntityDef(components=[Position], entity_id=1)],
    )
    assert_graph(actual_graph, "expected_graph_arithmetic.yaml")


# test compile basic arithmetic example with multiple entities
def test_graph_compile_arithmetic_multiple():
    def arithmetic_multiple_fn(g: Plotter):
        ms_in_sec = int(1e3)
        env = g.entity(components=[Clock])
        car = g.entity(
            components=[
                Position,
                Velocity,
            ]
        )
        tick_ms = env[Clock].tick_ms
        neg_xps = -car[Velocity].x
        x_delta = neg_xps * (tick_ms * ms_in_sec)
        car[Position].x = x_delta + car[Position].x

    actual_graph = compile_graph(
        convert_fn=arithmetic_multiple_fn,
        component_defs=[Position, Velocity, Clock],
        entity_defs=[
            EntityDef(components=[Position, Velocity], entity_id=1),
            EntityDef(components=[Clock], entity_id=2),
        ],
    )
    to_yaml_proto(actual_graph)

    assert_graph(actual_graph, "expected_graph_arithmetic_multiple.yaml")


# test compile ternary conditional
def test_graph_compile_ternary():
    def ternary_fn(g: Plotter):
        car = g.entity(
            components=[
                Position,
            ]
        )
        env = g.entity(components=[Clock])
        x_delta = 20 if env[Clock].tick_ms > 2000 else 10
        car[Position].x = x_delta

    actual_graph = compile_graph(
        convert_fn=ternary_fn,
        component_defs=[Position, Clock],
        entity_defs=[
            EntityDef(components=[Position], entity_id=1),
            EntityDef(components=[Clock], entity_id=2),
        ],
    )

    assert_graph(actual_graph, "expected_graph_ternary.yaml")


# test compile if else conditional
def test_graph_compile_ifelse():
    def ifelse_fn(g: Plotter):
        car = g.entity(
            components=[
                Position,
                Speed,
                Velocity,
            ]
        )
        env = g.entity(components=[Clock])
        if env[Clock].tick_ms > 2000:
            car[Position].x += g.min(car[Speed].max_x, 2 * car[Velocity].x)
            car[Position].y = car[Position].x + 2
        elif env[Clock].tick_ms > 5000:
            car[Position].x += g.min(car[Speed].max_x, 5 * car[Velocity].x)
            car[Position].y = car[Position].x + 10
        else:
            car[Position].x = g.min(car[Speed].max_x, 1 * car[Velocity].x)
            car[Position].y = car[Position].x - 5

    actual_graph = compile_graph(
        convert_fn=ifelse_fn,
        component_defs=[Position, Clock, Velocity, Speed],
        entity_defs=[
            EntityDef(components=[Position, Velocity, Speed], entity_id=1),
            EntityDef(components=[Clock], entity_id=2),
        ],
    )
    assert_graph(actual_graph, "expected_graph_ifelse.yaml")

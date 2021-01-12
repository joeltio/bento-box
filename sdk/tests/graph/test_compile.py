#
# Bentobox
# SDK - Graph Tests
# Test graph compilation @graph.compile
#

import yaml
from os import path
from google.protobuf.json_format import MessageToDict, ParseDict, MessageToJson
from typing import Callable, Any

from bento import graph
from bento.protos.graph_pb2 import Graph, Node
from bento.protos.references_pb2 import AttributeRef
from bento.graph.value import wrap_const
from bento.graph.plotter import Plotter

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
    assert MessageToJson(actual, sort_keys=True) == MessageToJson(
        expected, sort_keys=True
    )


## tests
# test that empty no op functions are compilable
def test_graph_compile_empty():
    @graph.compile_graph
    def actual_graph(g: Plotter):
        pass

    assert actual_graph == Graph()


# test compile basic arithmetic example with one entity
def test_graph_compile_arithmetic():
    @graph.compile_graph
    def actual_graph(g: Plotter):
        car = g.entity(
            components=[
                "position",
            ]
        )
        x_delta = 20
        car["position"].x += x_delta

    assert_graph(actual_graph, "expected_graph_arithmetic.yaml")


# test compile basic arithmetic example with multiple entities
def test_graph_compile_arithmetic_multiple():
    @graph.compile_graph
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
    @graph.compile_graph
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
    @graph.compile_graph
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

#
# Bentobox
# SDK - Graph Tests
# Test graph compilation @graph.compile
#

from bento import graph
from bento.protos.graph_pb2 import Graph
from bento.graph.plotter import Plotter

# test that empty no op functions are compilable
def test_graph_compile_empty():
    @graph.compile_graph
    def actual_graph(g: Plotter):
        pass

    assert actual_graph == Graph()


# test that constants get converted to constant nodes
def test_graph_compile_const():
    @graph.compile_graph
    def actual_graph(g: Plotter):
        car = g.entity(
            components=[
                "position",
            ]
        )
        x_delta = 20
        car["position"].x = car["position"].x + x_delta

    print(actual_graph.outputs)
    raise ValueError()


# test compile basic attrimatic example
def test_graph_compile_arithmetic():
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

    print(actual_graph.outputs)
    raise ValueError()


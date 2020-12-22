#
# Bentobox
# SDK - Graph Tests
# Test graph compilation @graph.compile
#

from bento import graph
from bento.protos.graph_pb2 import Graph, Node
from bento.protos.references_pb2 import AttributeRef
from bento.graph.value import wrap_const
from bento.graph.plotter import Plotter

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

    # TODO(mrzzy): compare with YAML test case to make this easier to test
    print(actual_graph.outputs)
    car_pos_x = actual_graph.outputs[0]
    attr, to_node = car_pos_x.mutate_attr, car_pos_x.to_node
    assert attr.component == "position" and attr.attribute == "x"
    assert to_node.add_op.x.retrieve_op.retrieve_attr.component == "position"
    assert to_node.add_op.x.retrieve_op.retrieve_attr.attribute == "x"
    assert to_node.add_op.y == wrap_const(20)


# test compile basic attrimatic example
# test compile basic attrimatic example with one entity
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

    print(actual_graph.outputs)

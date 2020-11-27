# Bentobox SDK - Graph
# Tests
# Test graph compilation @graph.compile
#

from bento import graph
from bento.protos.graph_pb2 import Graph
from bento.graph.plotter import Plotter

# test that empty no op functions are compilable
def test_graph_compile_empty():
    @graph.compile_graph
    def actual_graph(g: Plotter):
        g.graph
        pass

    assert actual_graph == Graph()

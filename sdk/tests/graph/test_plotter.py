#
# Bentobox
# SDK - Graph Tests
# Test graph compilation @graph.compile
#


from bento.value import wrap
from bento.protos.graph_pb2 import Graph, Node
from bento.protos.references_pb2 import AttributeRef
from bento.graph.plotter import Plotter

# sanity check empty plotter gives empty graph
def test_plotter_empty():
    g = Plotter()
    assert g.graph() == Graph()


# test that graph plotter can record a retrive, mutate operation
def test_plotter_retrieve_mutate_op():
    g = Plotter()
    person = g.entity(components=["position"])
    pos_x = person["position"].x
    person["position"].y = pos_x

    # check retrieve and mutate nodes correctly are set as graph inputs and outputs
    assert g.graph() == Graph(
        inputs=[
            Node.Retrieve(
                retrieve_attr=AttributeRef(
                    entity_id=person.id,
                    component="position",
                    attribute="x",
                )
            )
        ],
        outputs=[
            Node.Mutate(
                mutate_attr=AttributeRef(
                    entity_id=person.id,
                    component="position",
                    attribute="y",
                ),
                # check that mutation node recorded assignment correctly
                to_node=pos_x,
            ),
        ],
    )


# test that graph plotter can record switch condition and poolean ops
def test_plotter_conditional_boolean():
    g = Plotter()
    env = g.entity(components=["keyboard"])
    car = g.entity(components=["position"])

    key_pressed = env["keyboard"].pressed
    car_pos_x = g.switch(
        condition=g.eq(key_pressed, g.const("left")),
        true=g.const(-1.0),
        false=g.switch(
            condition=g.eq(key_pressed, g.const("right")),
            true=g.const(1.0),
            false=g.const(0.0),
        ),
    )
    car["position"].x = car_pos_x

    assert g.graph() == Graph(
        inputs=[
            Node.Retrieve(
                retrieve_attr=AttributeRef(
                    entity_id=env.id,
                    component="keyboard",
                    attribute="pressed",
                )
            )
        ],
        outputs=[
            Node.Mutate(
                mutate_attr=AttributeRef(
                    entity_id=car.id,
                    component="position",
                    attribute="x",
                ),
                # check that mutation node recorded assignment correctly
                to_node=car_pos_x,
            ),
        ],
    )

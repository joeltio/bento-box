#
# Bentobox
# SDK - Graph Tests
# Test graph compilation @graph.compile
#


from bento.value import wrap
from bento.ecs.graph import GraphEntity
from bento.protos.graph_pb2 import Graph, Node
from bento.protos.references_pb2 import AttributeRef
from bento.graph.plotter import Plotter
from tests.components import Position, Keyboard

# sanity check empty plotter gives empty graph
def test_graph_plotter_empty():
    g = Plotter()
    assert g.graph() == Graph()


# test that graph plotter can record a retrieve, mutate operation
def test_graph_plotter_retrieve_mutate_op():
    g = Plotter(entities=[GraphEntity(components=["position"], entity_id=1)])
    person = g.entity(components=[Position])
    pos_x = person[Position].x
    person[Position].y = pos_x

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
                to_node=pos_x.node,
            ),
        ],
    )


# test that graph plotter can record switch condition and boolean ops
def test_graph_plotter_conditional_boolean():
    g = Plotter(
        entities=[
            GraphEntity(components=["position"], entity_id=1),
            GraphEntity(components=["keyboard"], entity_id=2),
        ]
    )
    env = g.entity(components=[Keyboard])
    car = g.entity(components=[Position])

    key_pressed = env[Keyboard].pressed
    car_pos_x = g.switch(
        condition=key_pressed == "left",
        true=-1.0,
        false=g.switch(
            condition=key_pressed == "right",
            true=1.0,
            false=0.0,
        ),
    )
    car[Position].x = car_pos_x

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
                to_node=car_pos_x.node,
            ),
        ],
    )

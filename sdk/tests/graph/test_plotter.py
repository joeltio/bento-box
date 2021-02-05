#
# Bentobox
# SDK - Graph Tests
# Test graph compilation @graph.compile


from bento.value import wrap
from bento.ecs.spec import EntityDef, ComponentDef
from bento.ecs.graph import GraphEntity, GraphComponent
from bento.protos.graph_pb2 import Graph, Node
from bento.protos.references_pb2 import AttributeRef
from bento.graph.plotter import Plotter
from bento.example.specs import Position, Keyboard

# sanity check empty plotter gives empty graph
def test_graph_plotter_empty():
    g = Plotter(entity_defs=[], component_defs=[])
    assert g.graph() == Graph()


# test that graph plotter can record a retrieve, mutate operation
def test_graph_plotter_retrieve_mutate_op():
    entity_id = 1
    g = Plotter(
        entity_defs=[
            EntityDef(components=[Position.name], entity_id=1),
        ],
        component_defs=[Position],
    )
    person = g.entity(components=[Position])
    pos_x = person[Position].x
    person[Position].y = pos_x

    # check retrieve and mutate nodes correctly are set as graph inputs and outputs
    assert g.graph() == Graph(
        inputs=[
            Node.Retrieve(
                retrieve_attr=AttributeRef(
                    entity_id=entity_id,
                    component=Position.name,
                    attribute="x",
                )
            )
        ],
        outputs=[
            Node.Mutate(
                mutate_attr=AttributeRef(
                    entity_id=entity_id,
                    component=Position.name,
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
        entity_defs=[
            EntityDef(components=[Position], entity_id=1),
            EntityDef(components=[Keyboard], entity_id=2),
        ],
        component_defs=[Position, Keyboard],
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
                    component=Keyboard.name,
                    attribute="pressed",
                )
            )
        ],
        outputs=[
            Node.Mutate(
                mutate_attr=AttributeRef(
                    entity_id=car.id,
                    component=Position.name,
                    attribute="x",
                ),
                # check that mutation node recorded assignment correctly
                to_node=car_pos_x.node,
            ),
        ],
    )

#
# Bentobox
# SDK - Graph Tests
# Test graph compilation @graph.compile


from bento.ecs.graph import GraphComponent, GraphEntity
from bento.ecs.spec import ComponentDef, EntityDef
from bento.example.specs import Keyboard, Position, Velocity
from bento.graph.plotter import Plotter
from bento.graph.spec import Graph
from bento.protos.graph_pb2 import Node
from bento.protos.references_pb2 import AttributeRef
from bento.value import wrap

# sanity check empty plotter gives empty graph
def test_graph_plotter_empty():
    g = Plotter(entity_defs=[], component_defs=[])
    assert g.graph() == Graph()


# test that graph plotter can record a retrieve, mutate operation
def test_graph_plotter_retrieve_mutate_op():
    entity_id = 1
    g = Plotter(
        entity_defs=[
            EntityDef(components=[Position], entity_id=1),
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


# test graph plotter produces graphs with inputs and outputs sorted by order appearance in code
def test_graph_plotter_preserve_code_order():
    g = Plotter(
        entity_defs=[
            EntityDef(components=[Position, Velocity], entity_id=1),
        ],
        component_defs=[Position, Velocity],
    )

    car = g.entity(components=[Position, Velocity])
    # since Velocity.x is used first, it should appear in inputs before Position.x
    car_velocity_x = car[Velocity].x
    car_pos_x = car[Position].x
    # since Velocity.x is modified last, it should appear in outputs after Position.x
    car[Position].x = 3
    car[Velocity].x = 2

    position_x = car[Position].x
    velocity_x = car[Velocity].x

    assert (
        g.graph().yaml
        == Graph(
            inputs=[
                Node.Retrieve(
                    retrieve_attr=AttributeRef(
                        entity_id=car.id,
                        component=Velocity.name,
                        attribute="x",
                    )
                ),
                Node.Retrieve(
                    retrieve_attr=AttributeRef(
                        entity_id=car.id,
                        component=Position.name,
                        attribute="x",
                    )
                ),
            ],
            outputs=[
                Node.Mutate(
                    mutate_attr=AttributeRef(
                        entity_id=car.id,
                        component=Position.name,
                        attribute="x",
                    ),
                    to_node=position_x.node,
                ),
                Node.Mutate(
                    mutate_attr=AttributeRef(
                        entity_id=car.id,
                        component=Velocity.name,
                        attribute="x",
                    ),
                    to_node=velocity_x.node,
                ),
            ],
        ).yaml
    )

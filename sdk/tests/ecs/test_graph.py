#
# Bentobox
# SDK - Graph
# Graph ECS
#

from typing import Set
from bento.ecs.spec import ComponentDef, EntityDef
from bento.ecs.graph import GraphEntity, GraphComponent, GraphNode, wrap_const
from bento.protos.graph_pb2 import Node
from bento.protos.references_pb2 import AttributeRef
from bento.example.specs import Position


def test_graph_ecs_entity():
    components = [GraphComponent.from_def(entity_id=1, component_def=Position)]
    entity = GraphEntity(components=components, entity_id=1)
    # check Entity's components accessible via `.components`
    assert [c.component_name for c in entity.components] == [Position.name]
    # check component accessible by name using [] notation
    position = entity[Position]
    assert isinstance(position, GraphComponent)


def test_graph_ecs_entity_from_def():
    entity_id = 1
    car = GraphEntity.from_def(
        entity_def=EntityDef(components=[Position.name], entity_id=1),
        component_defs=[Position],
    )
    assert car.id == entity_id
    # check Entity's components accessible via `.components`
    assert [c.component_name for c in car.components] == [Position.name]

    # test that we cannnot create from EntityDef with unset id
    has_error = False
    try:
        GraphEntity.from_def(EntityDef([]), [])
    except ValueError:
        has_error = True
    assert has_error


def test_graph_ecs_component_from_def():
    entity_id = 1
    position = GraphComponent.from_def(entity_id, Position)
    assert position.component_name == Position.name

    # test that we cannnot create from ComponentDef with unset name
    has_error = False
    try:
        GraphComponent.from_def(entity_id, ComponentDef("", {}))
    except ValueError:
        has_error = True
    assert has_error


def test_graph_ecs_component_get_attr():
    entity_id = 1
    position = GraphComponent.from_def(entity_id, Position)
    # check that getting an attribute from a component returns a GraphNode
    # wrapping a Retrieve node that retrieves the attribute
    pos_x = position.x
    expected_node = Node(
        retrieve_op=Node.Retrieve(
            retrieve_attr=AttributeRef(
                entity_id=entity_id, component=Position.name, attribute="x"
            )
        )
    )
    assert pos_x.node == expected_node
    # check that component records the retrieve in `.inputs`
    assert position.inputs[0].node == expected_node
    # check that retrieving the same attribute only records it once
    pos_y = position.x
    assert len(position.inputs) == 1


def test_graph_ecs_component_set_attr_node():
    entity_id = 1
    position = GraphComponent.from_def(entity_id, Position)
    pos_x = position.x
    position.y = 10
    # check setting attribute to node sets expected output node.
    position.y = pos_x
    expected_node = Node(
        mutate_op=Node.Mutate(
            mutate_attr=AttributeRef(
                entity_id=entity_id,
                component=Position.name,
                attribute="y",
            ),
            to_node=pos_x.node,
        )
    )
    assert position.outputs[0].node == expected_node
    # check that setting attribute only takes the last definition
    # the first definition should be ignored since the attribute is redefined
    assert len(position.outputs) == 1


def test_graph_ecs_component_set_attr_native_value():
    entity_id = 1
    position = GraphComponent.from_def(entity_id, Position)
    # check setting attribute to native sets expected output node node.
    position.y = 3
    expected_node = Node(
        mutate_op=Node.Mutate(
            mutate_attr=AttributeRef(
                entity_id=entity_id,
                component=Position.name,
                attribute="y",
            ),
            to_node=wrap_const(3),
        )
    )
    assert position.outputs[0].node == expected_node


def test_graph_ecs_component_aug_assign_node():
    entity_id = 1
    position = GraphComponent.from_def(entity_id, Position)
    # check augment assignment flags the attribute (position.x) as both input and output
    position.y += 30
    attr_ref = AttributeRef(
        entity_id=entity_id,
        component=Position.name,
        attribute="y",
    )
    expected_input = Node(retrieve_op=Node.Retrieve(retrieve_attr=attr_ref))
    expected_output = Node(
        mutate_op=Node.Mutate(
            mutate_attr=attr_ref,
            to_node=Node(
                add_op=Node.Add(
                    x=expected_input,
                    y=wrap_const(30),
                )
            ),
        )
    )
    assert len(position.inputs) == 1
    assert position.inputs[0].node == expected_input
    assert len(position.outputs) == 1
    assert position.outputs[0].node == expected_output


def test_graph_ecs_node_wrap():
    wrap_cases = [
        ["w", GraphNode(node=wrap_const("w"))],
        [wrap_const(1), GraphNode(node=wrap_const(1))],
        [GraphNode(node=wrap_const(True)), GraphNode(node=wrap_const(True))],
    ]

    for val, expected in wrap_cases:
        assert GraphNode.wrap(val) == expected

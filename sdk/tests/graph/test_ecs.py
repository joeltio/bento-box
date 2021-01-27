#
# Bentobox
# SDK - Graph
# Graph ECS
#

from bento.ecs.graph import *


def test_graph_ecs_entity():
    components = ["position"]
    entity = GraphEntity(components=components)
    # check Entity's components accessible via `.components`
    assert len(set(c._name for c in entity.components) - set(components)) == 0
    # check component accessible by name using [] notation
    position = entity[components[0]]
    assert isinstance(position, GraphComponent)


def test_graph_ecs_component_get_attr():
    entity_id, name = 1, "position"
    position = GraphComponent(entity_id=entity_id, name=name)
    # check that getting an attribute from a component returns a GraphNode
    # wrapping a Retrieve node that retrieves the attribute
    pos_x = position.x
    expected_node = Node(
        retrieve_op=Node.Retrieve(
            retrieve_attr=AttributeRef(
                entity_id=entity_id, component=name, attribute="x"
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
    entity_id, name = 1, "position"
    position = GraphComponent(entity_id=entity_id, name=name)
    pos_x = position.x
    position.y = 10
    # check setting attribute to node sets expected output node.
    position.y = pos_x
    expected_node = Node(
        mutate_op=Node.Mutate(
            mutate_attr=AttributeRef(
                entity_id=entity_id,
                component="position",
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
    entity_id, name = 1, "position"
    position = GraphComponent(entity_id=entity_id, name=name)
    # check setting attribute to native sets expected output node node.
    position.y = 3.1
    expected_node = Node(
        mutate_op=Node.Mutate(
            mutate_attr=AttributeRef(
                entity_id=entity_id,
                component="position",
                attribute="y",
            ),
            to_node=wrap_const(3.1),
        )
    )
    assert position.outputs[0].node == expected_node


def test_graph_ecs_component_aug_assign_node():
    entity_id, name = 1, "position"
    position = GraphComponent(entity_id=entity_id, name=name)
    # check augment assignment flags the attribute (position.x) as both input and output
    position.y += 30
    attr_ref = AttributeRef(
        entity_id=entity_id,
        component="position",
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

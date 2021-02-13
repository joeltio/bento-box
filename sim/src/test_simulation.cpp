#include <test_simulation.h>

namespace test_simulation {

TestComponent::TestComponent(int width, int height)
    : UserComponent(TEST_COMPONENT_NAME, createCompDef()) {
    auto widthVal = bento::protos::Value();
    widthVal.mutable_primitive()->set_int_64(width);
    widthVal.mutable_data_type()->set_primitive(
        bento::protos::Type_Primitive_INT64);
    setValue("width", widthVal);

    auto heightVal = bento::protos::Value();
    heightVal.mutable_primitive()->set_int_64(height);
    heightVal.mutable_data_type()->set_primitive(
        bento::protos::Type_Primitive_INT64);
    setValue("height", heightVal);
}

bento::protos::SystemDef cycle100System(
    const bento::protos::AttributeRef& attrRef) {
    // Set increment height from 0 to 100 then wrap to 0
    auto attrRetrieve = bento::protos::Node();
    attrRetrieve.mutable_retrieve_op()->mutable_retrieve_attr()->CopyFrom(
        attrRef);

    // Create condition
    auto maxHeightConst = bento::protos::Node();
    auto maxHeightVal = maxHeightConst.mutable_const_op()->mutable_held_value();
    maxHeightVal->mutable_primitive()->set_int_64(100);
    maxHeightVal->mutable_data_type()->set_primitive(
        bento::protos::Type_Primitive_INT64);
    auto condNode = bento::protos::Node();
    condNode.mutable_gt_op()->mutable_x()->CopyFrom(attrRetrieve);
    condNode.mutable_gt_op()->mutable_y()->CopyFrom(maxHeightConst);

    // Create switch
    auto startHeightConst = bento::protos::Node();
    auto startHeightVal =
        startHeightConst.mutable_const_op()->mutable_held_value();
    startHeightVal->mutable_primitive()->set_int_64(0);
    startHeightVal->mutable_data_type()->set_primitive(
        bento::protos::Type_Primitive_INT64);
    auto incrementHeightConst = bento::protos::Node();
    auto incrementHeightVal =
        incrementHeightConst.mutable_const_op()->mutable_held_value();
    incrementHeightVal->mutable_primitive()->set_int_64(1);
    incrementHeightVal->mutable_data_type()->set_primitive(
        bento::protos::Type_Primitive_INT64);

    auto nextHeight = bento::protos::Node();
    nextHeight.mutable_add_op()->mutable_x()->CopyFrom(attrRetrieve);
    nextHeight.mutable_add_op()->mutable_y()->CopyFrom(incrementHeightConst);

    auto switchNode = bento::protos::Node();
    switchNode.mutable_switch_op()->mutable_condition_node()->CopyFrom(
        condNode);
    switchNode.mutable_switch_op()->mutable_true_node()->CopyFrom(
        startHeightConst);
    switchNode.mutable_switch_op()->mutable_false_node()->CopyFrom(nextHeight);

    auto mutateNode = bento::protos::Node_Mutate();
    mutateNode.mutable_mutate_attr()->CopyFrom(attrRef);
    mutateNode.mutable_to_node()->CopyFrom(switchNode);

    auto systemDef = bento::protos::SystemDef();
    systemDef.set_id(1);
    systemDef.mutable_graph()->mutable_outputs()->Add(std::move(mutateNode));
    systemDef.mutable_graph()->mutable_inputs()->Add(
        bento::protos::Node_Retrieve(attrRetrieve.retrieve_op()));

    return systemDef;
}

TestSimulation::TestSimulation() {
    // Create entity def
    ics::index::EntityIndex::EntityId entityId = 1;
    entityDef.set_id(entityId);
    entityDef.mutable_components()->Add(std::string(compDef.name()));

    simDef.set_name(SIM_NAME);
    simDef.mutable_components()->Add(bento::protos::ComponentDef(compDef));
    simDef.mutable_entities()->Add(bento::protos::EntityDef(entityDef));
    auto sys = cycle100System(
        interpreter::createAttrRef(compDef.name().c_str(), entityId, "height"));
    simDef.mutable_systems()->Add()->CopyFrom(sys);

    // Setup the init Graph
    auto initGraph = bento::protos::Graph();

    // Create a const node for the starting value of the width and height
    auto startValNode = bento::protos::Node();
    startValNode.mutable_const_op()
        ->mutable_held_value()
        ->mutable_primitive()
        ->set_int_64(COMP_START_VAL);
    startValNode.mutable_const_op()
        ->mutable_held_value()
        ->mutable_data_type()
        ->set_primitive(bento::protos::Type_Primitive_INT64);

    // Set height to startValNode's value
    auto heightRef =
        interpreter::createAttrRef(compDef.name().c_str(), entityId, "height");
    auto setHeightNode = bento::protos::Node_Mutate();
    setHeightNode.mutable_mutate_attr()->CopyFrom(heightRef);
    setHeightNode.mutable_to_node()->CopyFrom(startValNode);
    auto getHeightNode = bento::protos::Node_Retrieve();
    getHeightNode.mutable_retrieve_attr()->CopyFrom(heightRef);

    // Set width to startValNode's value
    auto widthRef =
        interpreter::createAttrRef(compDef.name().c_str(), entityId, "width");
    auto setWidthNode = bento::protos::Node_Mutate();
    setWidthNode.mutable_mutate_attr()->CopyFrom(widthRef);
    setWidthNode.mutable_to_node()->CopyFrom(startValNode);
    auto getWidthNode = bento::protos::Node_Retrieve();
    getWidthNode.mutable_retrieve_attr()->CopyFrom(widthRef);

    // Add the references to the graph
    initGraph.mutable_inputs()->Add()->CopyFrom(getHeightNode);
    initGraph.mutable_inputs()->Add()->CopyFrom(getWidthNode);

    // Add the mutate nodes to the graph
    initGraph.mutable_outputs()->Add()->CopyFrom(setHeightNode);
    initGraph.mutable_outputs()->Add()->CopyFrom(setWidthNode);

    simDef.mutable_init_graph()->CopyFrom(initGraph);
}

}  // namespace test_simulation

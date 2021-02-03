#include <test_simulation.h>

namespace test_simulation {

TestComponent::TestComponent(int width, int height)
    : UserComponent(TEST_COMPONENT_NAME, createCompDef()) {
    auto widthVal = bento::protos::Value();
    widthVal.mutable_primitive()->set_int_64(width);
    setValue("width", widthVal);

    auto heightVal = bento::protos::Value();
    heightVal.mutable_primitive()->set_int_64(height);
    setValue("height", heightVal);
}

bento::protos::ComponentDef testCompDef() {
    return interpreter::createSimpleCompDef(
        TEST_COMPONENT_NAME, {{"height", bento::protos::Type_Primitive_INT64},
                              {"width", bento::protos::Type_Primitive_INT64}});
}

bento::protos::SimulationDef testSimDef() {
    // Create comp def
    auto compDef = TestComponent().compDef;

    // Create entity def
    auto entityDef = bento::protos::EntityDef();
    entityDef.set_id(1);
    entityDef.mutable_components()->Add(std::string(compDef.name()));

    // Create system def
    // Set increment height from 0 to 100 then wrap to 0
    auto heightRef =
        interpreter::createAttrRef(compDef.name().c_str(), 1, "height");
    auto heightRetrieve = bento::protos::Node();
    heightRetrieve.mutable_retrieve_op()->mutable_retrieve_attr()->CopyFrom(
        heightRef);

    // Create condition
    auto maxHeightConst = bento::protos::Node();
    maxHeightConst.mutable_const_op()
        ->mutable_held_value()
        ->mutable_primitive()
        ->set_int_32(100);
    auto condNode = bento::protos::Node();
    condNode.mutable_gt_op()->mutable_x()->CopyFrom(heightRetrieve);
    condNode.mutable_gt_op()->mutable_y()->CopyFrom(maxHeightConst);

    // Create switch
    auto startHeightConst = bento::protos::Node();
    startHeightConst.mutable_const_op()
        ->mutable_held_value()
        ->mutable_primitive()
        ->set_int_32(0);
    auto incrementHeightConst = bento::protos::Node();
    incrementHeightConst.mutable_const_op()
        ->mutable_held_value()
        ->mutable_primitive()
        ->set_int_32(1);

    auto nextHeight = bento::protos::Node();
    nextHeight.mutable_add_op()->mutable_x()->CopyFrom(heightRetrieve);
    nextHeight.mutable_add_op()->mutable_y()->CopyFrom(incrementHeightConst);

    auto switchNode = bento::protos::Node();
    switchNode.mutable_switch_op()->mutable_condition_node()->CopyFrom(
        condNode);
    switchNode.mutable_switch_op()->mutable_true_node()->CopyFrom(
        startHeightConst);
    switchNode.mutable_switch_op()->mutable_false_node()->CopyFrom(nextHeight);

    auto mutateNode = bento::protos::Node_Mutate();
    mutateNode.mutable_mutate_attr()->CopyFrom(heightRef);
    mutateNode.mutable_to_node()->CopyFrom(switchNode);

    auto systemDef = bento::protos::SystemDef();
    systemDef.set_id(1);
    systemDef.mutable_graph()->mutable_outputs()->Add(std::move(mutateNode));
    systemDef.mutable_graph()->mutable_inputs()->Add(
        bento::protos::Node_Retrieve(heightRetrieve.retrieve_op()));

    auto simDef = bento::protos::SimulationDef();
    simDef.set_name("test simulation");
    simDef.mutable_components()->Add(std::move(compDef));
    simDef.mutable_entities()->Add(std::move(entityDef));
    simDef.mutable_systems()->Add(std::move(systemDef));

    return simDef;
}

}  // namespace test_simulation

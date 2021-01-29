#include <gtest/gtest.h>
#include <interpreter/graphInterpreter.h>
#include <interpreter/operations.h>

#include <bento/protos/ecs.pb.h>
#include <component/userComponent.h>
#include <ics.h>

#include <cmath>

#define TEST_SUITE GraphInterpreter

using namespace interpreter;

// Define a component
namespace {
const char TEST_COMPONENT_NAME[] = "TestComponent";
bento::protos::ComponentDef createCompDef() {
    auto compDef = bento::protos::ComponentDef();
    compDef.set_name(TEST_COMPONENT_NAME);

    auto& schema = *compDef.mutable_schema();
    schema["height"] = bento::protos::Type();
    schema["height"].set_primitive(bento::protos::Type_Primitive_INT64);

    schema["width"] = bento::protos::Type();
    schema["width"].set_primitive(bento::protos::Type_Primitive_INT64);
    return compDef;
}

struct TestComponent : public ics::component::UserComponent {
    TestComponent() : UserComponent(TEST_COMPONENT_NAME, createCompDef()) {}
    TestComponent(int width, int height)
        : UserComponent(TEST_COMPONENT_NAME, createCompDef()) {
        auto widthVal = bento::protos::Value();
        widthVal.mutable_primitive()->set_int_64(width);
        setValue("width", widthVal);

        auto heightVal = bento::protos::Value();
        heightVal.mutable_primitive()->set_int_64(height);
        setValue("height", heightVal);
    }
};

}  // namespace

class StoresFixture : public ::testing::Test {
   protected:
    ics::ComponentStore compStore;
    ics::index::IndexStore indexStore;
    // First entity
    ics::index::EntityIndex::EntityId entity1Id =
        indexStore.entity.addEntityId();
    TestComponent comp1{50, 30};

    // Second entity
    ics::index::EntityIndex::EntityId entity2Id =
        indexStore.entity.addEntityId();
    TestComponent comp2{90, 10};

    static bento::protos::AttributeRef createAttrRef(
        ics::index::EntityIndex::EntityId entityId, const char* attrName) {
        auto attrRef = bento::protos::AttributeRef();
        attrRef.set_component(TEST_COMPONENT_NAME);
        attrRef.set_entity_id(entityId);
        attrRef.set_attribute(attrName);
        return attrRef;
    }

    void SetUp() override {
        // Add the components
        auto comp1StoreId = ics::addComponent(indexStore, compStore, comp1);
        auto comp2StoreId = ics::addComponent(indexStore, compStore, comp2);

        // Add the components to the entities
        indexStore.entity.addComponent(entity1Id, comp1StoreId);
        indexStore.entity.addComponent(entity2Id, comp2StoreId);
    }

    void TearDown() override {
        // No teardown code is needed. Googletest will clean up all objects
        // automatically. The component values will be reset at the end of each
        // test.
    }
};

TEST_F(StoresFixture, RetrieveNode) {
    // Create the attribute ref
    auto attrRef = createAttrRef(entity1Id, "width");

    auto node = bento::protos::Node();
    auto retrieveAttr = node.mutable_retrieve_op()->mutable_retrieve_attr();
    retrieveAttr->set_component(TEST_COMPONENT_NAME);
    retrieveAttr->set_entity_id(entity1Id);
    retrieveAttr->set_attribute("width");

    auto value = evaluateNode(compStore, indexStore, node);
    ASSERT_EQ(value.primitive().int_64(),
              comp1.getValue("width").primitive().int_64());
}

TEST_F(StoresFixture, MutateNode) {
    auto node = bento::protos::Node_Mutate();
    // Set attribute to mutate
    auto mutateAttr = node.mutable_mutate_attr();
    mutateAttr->set_component(TEST_COMPONENT_NAME);
    mutateAttr->set_entity_id(entity1Id);
    mutateAttr->set_attribute("width");
    // Set value to change to
    int newVal = 1000;
    node.mutable_to_node()
        ->mutable_const_op()
        ->mutable_held_value()
        ->mutable_primitive()
        ->set_int_64(newVal);

    // Make sure that this test is valid by ensuring that the value to change to
    // is not the default value
    ASSERT_NE(newVal, comp1.getValue("width").primitive().int_64());

    // Mutate the value
    mutateOp(compStore, indexStore, node);

    auto& comp = ics::getComponent(indexStore, compStore, TEST_COMPONENT_NAME,
                                   entity1Id);
    ASSERT_EQ(comp.getValue("width").primitive().int_64(), newVal);
}

TEST_F(StoresFixture, SwitchNode) {
    auto node = bento::protos::Node();
    auto switchOpNode = node.mutable_switch_op();
    // Set the true and false nodes
    int trueVal = 10;
    int falseVal = 30;
    switchOpNode->mutable_true_node()
        ->mutable_const_op()
        ->mutable_held_value()
        ->mutable_primitive()
        ->set_int_64(trueVal);
    switchOpNode->mutable_false_node()
        ->mutable_const_op()
        ->mutable_held_value()
        ->mutable_primitive()
        ->set_int_64(falseVal);

    // Set the condition node value
    auto conditionNode = switchOpNode->mutable_condition_node();
    auto condVal = conditionNode->mutable_const_op()->mutable_held_value();
    // Set the condition as boolean with true
    condVal->mutable_primitive()->set_boolean(true);
    condVal->mutable_data_type()->set_primitive(
        bento::protos::Type_Primitive_BOOL);

    ASSERT_EQ(evaluateNode(compStore, indexStore, node).primitive().int_64(),
              trueVal);

    // Set the condition to false
    condVal->mutable_primitive()->set_boolean(false);
    ASSERT_EQ(evaluateNode(compStore, indexStore, node).primitive().int_64(),
              falseVal);
}

TEST_F(StoresFixture, AddNode) {
    auto node = bento::protos::Node();
    auto addOpNode = node.mutable_add_op();
    // Set values to add
    int x = 10;
    int y = 30;

    addOpNode->mutable_x()
        ->mutable_const_op()
        ->mutable_held_value()
        ->mutable_primitive()
        ->set_int_64(x);
    addOpNode->mutable_y()
        ->mutable_const_op()
        ->mutable_held_value()
        ->mutable_primitive()
        ->set_int_64(y);

    ASSERT_EQ(evaluateNode(compStore, indexStore, node).primitive().int_64(),
              x + y);
}

TEST_F(StoresFixture, DivNodeFloorDividesInts) {
    auto node = bento::protos::Node();
    auto divOpNode = node.mutable_div_op();

    auto xVal = divOpNode->mutable_x()
                    ->mutable_const_op()
                    ->mutable_held_value()
                    ->mutable_primitive();
    auto yVal = divOpNode->mutable_y()
                    ->mutable_const_op()
                    ->mutable_held_value()
                    ->mutable_primitive();

    // Division of integers should be floored
    xVal->set_int_64(10);
    yVal->set_int_64(30);
    ASSERT_EQ(evaluateNode(compStore, indexStore, node).primitive().int_64(),
              0);

    xVal->set_int_64(4);
    yVal->set_int_64(3);
    ASSERT_EQ(evaluateNode(compStore, indexStore, node).primitive().int_64(),
              1);
}

TEST_F(StoresFixture, DivNodeFloatDivide) {
    auto node = bento::protos::Node();
    auto divOpNode = node.mutable_div_op();

    auto xVal = divOpNode->mutable_x()
                    ->mutable_const_op()
                    ->mutable_held_value()
                    ->mutable_primitive();
    auto yVal = divOpNode->mutable_y()
                    ->mutable_const_op()
                    ->mutable_held_value()
                    ->mutable_primitive();

    xVal->set_float_64(1.0f);
    yVal->set_float_64(3.0f);
    ASSERT_FLOAT_EQ(
        evaluateNode(compStore, indexStore, node).primitive().float_64(),
        1.0f / 3.0f);
}

TEST_F(StoresFixture, MaxNode) {
    auto node = bento::protos::Node();
    auto maxOpNode = node.mutable_max_op();

    auto xVal = maxOpNode->mutable_x()
                    ->mutable_const_op()
                    ->mutable_held_value()
                    ->mutable_primitive();
    auto yVal = maxOpNode->mutable_y()
                    ->mutable_const_op()
                    ->mutable_held_value()
                    ->mutable_primitive();

    xVal->set_int_64(10);
    yVal->set_int_64(30);
    ASSERT_EQ(evaluateNode(compStore, indexStore, node).primitive().int_64(),
              30);
}

TEST_F(StoresFixture, MinNode) {
    auto node = bento::protos::Node();
    auto minOpNode = node.mutable_min_op();

    auto xVal = minOpNode->mutable_x()
                    ->mutable_const_op()
                    ->mutable_held_value()
                    ->mutable_primitive();
    auto yVal = minOpNode->mutable_y()
                    ->mutable_const_op()
                    ->mutable_held_value()
                    ->mutable_primitive();

    xVal->set_int_64(10);
    yVal->set_int_64(30);
    ASSERT_EQ(evaluateNode(compStore, indexStore, node).primitive().int_64(),
              10);
}

TEST_F(StoresFixture, AbsNode) {
    auto node = bento::protos::Node();
    auto absOpNode = node.mutable_abs_op();

    auto val = absOpNode->mutable_x()
                   ->mutable_const_op()
                   ->mutable_held_value()
                   ->mutable_primitive();

    val->set_int_64(10);
    ASSERT_EQ(evaluateNode(compStore, indexStore, node).primitive().int_64(),
              10);
    val->set_int_64(-10);
    ASSERT_EQ(evaluateNode(compStore, indexStore, node).primitive().int_64(),
              10);
}

TEST_F(StoresFixture, FloorNode) {
    auto node = bento::protos::Node();
    auto floorOpNode = node.mutable_floor_op();

    auto val = floorOpNode->mutable_x()
                   ->mutable_const_op()
                   ->mutable_held_value()
                   ->mutable_primitive();

    val->set_float_64(1.98f);
    ASSERT_FLOAT_EQ(
        evaluateNode(compStore, indexStore, node).primitive().float_64(), 1.0f);
    val->set_float_64(1.3f);
    ASSERT_FLOAT_EQ(
        evaluateNode(compStore, indexStore, node).primitive().float_64(), 1.0f);
}

TEST_F(StoresFixture, CeilNode) {
    auto node = bento::protos::Node();
    auto ceilOpNode = node.mutable_ceil_op();

    auto val = ceilOpNode->mutable_x()
                   ->mutable_const_op()
                   ->mutable_held_value()
                   ->mutable_primitive();

    val->set_float_64(1.3f);
    ASSERT_FLOAT_EQ(
        evaluateNode(compStore, indexStore, node).primitive().float_64(), 2.0f);
    val->set_float_64(1.98f);
    ASSERT_FLOAT_EQ(
        evaluateNode(compStore, indexStore, node).primitive().float_64(), 2.0f);
}

TEST_F(StoresFixture, PowNode) {
    auto node = bento::protos::Node();
    auto powOpNode = node.mutable_pow_op();

    auto xVal = powOpNode->mutable_x()
                    ->mutable_const_op()
                    ->mutable_held_value()
                    ->mutable_primitive();
    auto yVal = powOpNode->mutable_y()
                    ->mutable_const_op()
                    ->mutable_held_value()
                    ->mutable_primitive();

    xVal->set_float_64(1.3f);
    yVal->set_float_64(2.0f);
    ASSERT_FLOAT_EQ(
        evaluateNode(compStore, indexStore, node).primitive().float_64(),
        1.69f);
}

TEST_F(StoresFixture, ModNode) {
    auto node = bento::protos::Node();
    auto modOpNode = node.mutable_mod_op();

    auto xVal = modOpNode->mutable_x()
                    ->mutable_const_op()
                    ->mutable_held_value()
                    ->mutable_primitive();
    auto yVal = modOpNode->mutable_y()
                    ->mutable_const_op()
                    ->mutable_held_value()
                    ->mutable_primitive();

    // Modulo does not allow floating point values
    xVal->set_float_64(1.3f);
    yVal->set_float_64(2.0f);
    EXPECT_ANY_THROW(evaluateNode(compStore, indexStore, node));

    xVal->set_int_64(12);
    yVal->set_int_64(7);
    ASSERT_FLOAT_EQ(
        evaluateNode(compStore, indexStore, node).primitive().int_64(), 12 % 7);
}

TEST_F(StoresFixture, SinNode) {
    auto node = bento::protos::Node();
    auto sinOpNode = node.mutable_sin_op();

    auto xVal = sinOpNode->mutable_x()
                    ->mutable_const_op()
                    ->mutable_held_value()
                    ->mutable_primitive();

    xVal->set_float_64(1.0f);
    ASSERT_FLOAT_EQ(
        evaluateNode(compStore, indexStore, node).primitive().float_64(),
        sin(1.0f));
}

TEST_F(StoresFixture, ArcSinNode) {
    auto node = bento::protos::Node();
    auto arcSinOpNode = node.mutable_arcsin_op();

    auto xVal = arcSinOpNode->mutable_x()
                    ->mutable_const_op()
                    ->mutable_held_value()
                    ->mutable_primitive();

    xVal->set_float_64(1.0f);
    ASSERT_FLOAT_EQ(
        evaluateNode(compStore, indexStore, node).primitive().float_64(),
        asin(1.0f));

    // The valid domain of arcsin is [-1, 1]
    xVal->set_float_64(2.0f);
    EXPECT_ANY_THROW(evaluateNode(compStore, indexStore, node));
}

TEST_F(StoresFixture, RandomNode) {
    auto node = bento::protos::Node();
    auto randomOpNode = node.mutable_random_op();

    auto lowVal = randomOpNode->mutable_low()
                      ->mutable_const_op()
                      ->mutable_held_value()
                      ->mutable_primitive();

    auto highVal = randomOpNode->mutable_high()
                       ->mutable_const_op()
                       ->mutable_held_value()
                       ->mutable_primitive();

    lowVal->set_float_64(12.0f);
    highVal->set_float_64(13.0f);

    auto rawVal =
        evaluateNode(compStore, indexStore, node).primitive().float_64();
    ASSERT_GE(rawVal, lowVal->float_64());
    ASSERT_LE(rawVal, highVal->float_64());
}

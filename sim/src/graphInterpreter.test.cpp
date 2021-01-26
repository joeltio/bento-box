#include <gtest/gtest.h>
#include <graphInterpreter.h>

#include <bento/protos/ecs.pb.h>
#include <component/userComponent.h>
#include <ics.h>

#define TEST_SUITE GraphInterpreter

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
};
}  // namespace

TEST(TEST_SUITE, GetAndSetAttributeRef) {
    // Create a store
    ics::ComponentStore componentStore = ics::ComponentStore();
    ics::index::IndexStore indexStore = ics::index::IndexStore();

    // Create the component
    auto comp = TestComponent();

    auto height = bento::protos::Value();
    height.mutable_primitive()->set_int_64(30);
    comp.setValue("height", height);

    auto width = bento::protos::Value();
    width.mutable_primitive()->set_int_64(50);
    comp.setValue("width", width);

    auto compStoreId = ics::addComponent(indexStore, componentStore, comp);

    // Add the component to a entity ID
    auto entityId = indexStore.entity.addEntityId();
    indexStore.entity.addComponent(entityId, compStoreId);

    // Create the attribute ref
    auto attrRef = bento::protos::AttributeRef();
    attrRef.set_component(TEST_COMPONENT_NAME);
    attrRef.set_entity_id(entityId);
    attrRef.set_attribute("height");

    auto& cppAttrRef = getAttributeRef(attrRef, componentStore, indexStore);

    ASSERT_EQ(cppAttrRef.primitive().int_64(), height.primitive().int_64());

    // Modify through cppAttrRef
    cppAttrRef.mutable_primitive()->set_int_64(10);
    cppAttrRef = getAttributeRef(attrRef, componentStore, indexStore);
    ASSERT_EQ(cppAttrRef.primitive().int_64(), 10);
}

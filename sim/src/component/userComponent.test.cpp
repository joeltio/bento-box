#include <component/userComponent.h>
#include <core/ics/componentSet.h>
#include <gtest/gtest.h>

#define TEST_SUITE UserComponent

using namespace ics::component;

// Define a component
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

struct TestComponent : public UserComponent {
    TestComponent() : UserComponent(TEST_COMPONENT_NAME, createCompDef()) {}
};

TEST(TEST_SUITE, SetAndGetValues) {
    TestComponent comp;
    auto height = bento::protos::Value();
    height.mutable_primitive()->set_int_64(30);
    comp.setValue("height", height);

    auto width = bento::protos::Value();
    width.mutable_primitive()->set_int_64(50);
    comp.setValue("width", width);

    ASSERT_EQ(height.primitive().int_64(),
              comp.getValue("height").primitive().int_64());
    ASSERT_EQ(width.primitive().int_64(),
              comp.getValue("width").primitive().int_64());
    // Sanity check
    ASSERT_EQ(height.primitive().int_64(), 30);
}
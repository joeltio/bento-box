#include <gtest/gtest.h>
#include <interpreter/util.h>
#include <index/entityIndex.h>

#define TEST_SUITE InterpreterUtil

using namespace interpreter;

TEST(TEST_SUITE, CreateAttrRef) {
    ics::index::EntityIndex entityIndex;
    auto entityId = entityIndex.addEntityId();
    const char* compName = "helloComponent";
    const char* refName = "my_attribute";
    auto attrRef = createAttrRef(compName, entityId, refName);

    ASSERT_EQ(attrRef.component(), compName);
    ASSERT_EQ(attrRef.entity_id(), entityId);
    ASSERT_EQ(attrRef.attribute(), refName);
}

TEST(TEST_SUITE, CreateCompDef) {
    const char* compName = "MyComponent";
    auto compDef = createSimpleCompDef(
        compName, {
                      {"is_cool", bento::protos::Type_Primitive_BOOL},
                      {"height", bento::protos::Type_Primitive_INT64},
                  });

    ASSERT_EQ(compDef.name(), compName);
    ASSERT_EQ(compDef.schema().at("is_cool").primitive(),
              bento::protos::Type_Primitive_BOOL);
    ASSERT_EQ(compDef.schema().at("height").primitive(),
              bento::protos::Type_Primitive_INT64);
}

#include <gtest/gtest.h>
#include <core/ics/component.h>
#include <core/ics/componentSet.h>
#include <index/componentType.h>

#define TEST_SUITE ComponentType

using namespace ics::index;

struct TestComponent : public ics::BaseComponent {
    int height;
};

TEST(TEST_SUITE, AddAndRetrieveComponentType) {
    ComponentType index;
    auto group = index.addComponentType<TestComponent>();
    index.addComponentType<ics::BaseComponent>();
    ASSERT_EQ(index.getComponentType<TestComponent>(), group);
}

TEST(TEST_SUITE, CheckIfComponentTypeExists) {
    ComponentType index;
    ASSERT_FALSE(index.hasComponentType<TestComponent>());
    ASSERT_FALSE(index.hasComponentType<ics::BaseComponent>());

    index.addComponentType<TestComponent>();
    ASSERT_FALSE(index.hasComponentType<ics::BaseComponent>());
    ASSERT_TRUE(index.hasComponentType<TestComponent>());

    index.addComponentType<ics::BaseComponent>();
    ASSERT_TRUE(index.hasComponentType<ics::BaseComponent>());
}

TEST(TEST_SUITE, UseComponentTypeIsFilter) {
    ComponentType index;
    auto group = index.addComponentType<TestComponent>();
    auto filter = index.is<TestComponent>();

    ics::ComponentSet compSet;
    compSet.emplace(group, 2);
    compSet.emplace(group, 5);
    compSet.emplace(group, 13);
    compSet.emplace(group+1, 3);
    compSet.emplace(group+1, 7);

    auto filteredSet = filter(compSet);
    int cumProd = 1;
    for (auto pair : filteredSet) {
        ASSERT_EQ(pair.first, group);
        cumProd *= pair.second;
    }

    ASSERT_EQ(cumProd, 130);
}

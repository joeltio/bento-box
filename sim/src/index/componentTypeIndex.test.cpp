#include <component/userComponent.h>
#include <core/ics/componentSet.h>
#include <gtest/gtest.h>
#include <index/componentTypeIndex.h>

#define TEST_SUITE ComponentType

using namespace ics::index;

TEST(TEST_SUITE, AddAndRetrieveComponentType) {
    ComponentTypeIndex index;
    const std::string name = "TestComponent";
    auto group = index.addComponentType(name);

    index.addComponentType("BaseComponent");

    ASSERT_EQ(index.getComponentType(name), group);
}

TEST(TEST_SUITE, CheckIfComponentTypeExists) {
    ComponentTypeIndex index;
    ASSERT_FALSE(index.hasComponentType("TestComponent"));
    ASSERT_FALSE(index.hasComponentType("BasesComponent"));

    index.addComponentType("TestComponent");
    ASSERT_FALSE(index.hasComponentType("BaseComponent"));
    ASSERT_TRUE(index.hasComponentType("TestComponent"));

    index.addComponentType("BaseComponent");
    ASSERT_TRUE(index.hasComponentType("BaseComponent"));
}

TEST(TEST_SUITE, UseComponentTypeIsFilter) {
    ComponentTypeIndex index;
    auto group = index.addComponentType("TestComponent");
    auto filter = index.filterCompType("TestComponent");

    ics::ComponentSet compSet;
    compSet.emplace(group, 2);
    compSet.emplace(group, 5);
    compSet.emplace(group, 13);
    compSet.emplace(group + 1, 3);
    compSet.emplace(group + 1, 7);

    auto filteredSet = filter(compSet);
    int cumProd = 1;
    for (auto pair : filteredSet) {
        ASSERT_EQ(pair.first, group);
        cumProd *= pair.second;
    }

    ASSERT_EQ(cumProd, 130);
}

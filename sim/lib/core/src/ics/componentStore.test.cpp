#include <gtest/gtest.h>
#include <core/ics/component.h>
#include <core/ics/compVec.h>
#include <core/ics/componentStore.h>

#define TEST_SUITE ComponentStoreTest

using namespace ics;

struct TestComponent : public BaseComponent {
    int height;
};

TEST(TEST_SUITE, CreateVec) {
    ComponentStore store;

    ASSERT_EQ(store.size(), 0);
    createCompVec<TestComponent>(store, 1);
    ASSERT_EQ(store.size(), 1);
}

TEST(TEST_SUITE, CreateCompVecReturnsReference) {
    ComponentStore store;
    auto& vec = createCompVec<TestComponent>(store, 1);
    vec.add(TestComponent { true, 20 });

    auto retrievedVec = std::any_cast<CompVec<BaseComponent>>(*store.at(1));
    ASSERT_EQ(retrievedVec.size(), 1);
}

TEST(TEST_SUITE, GetComponentsRetrievesComponents) {
    ComponentStore store;
    auto& vec = createCompVec<TestComponent>(store, 1);
    auto compId = vec.add(TestComponent { true, 20 });

    auto retrievedVec = getCompVec<TestComponent>(store, 1);
    ASSERT_EQ(retrievedVec.at(compId).height, 20);
}

TEST(TEST_SUITE, GetComponentsRetrievesComponentsByReference) {
    ComponentStore store;
    createCompVec<TestComponent>(store, 1);

    auto& vec1 = getCompVec<TestComponent>(store, 1);
    vec1.add(TestComponent { true, 20 });
    auto& vec2 = getCompVec<TestComponent>(store, 1);
    ASSERT_EQ(vec2.size(), 1);
}

TEST(TEST_SUITE, AddComponentsCreatesNewVec) {
    ComponentStore store;
    ASSERT_EQ(store.size(), 0);
    addComponent(store, TestComponent { true, 20 }, 1);
    ASSERT_EQ(store.size(), 1);
}

TEST(TEST_SUITE, AddComponentsAppendsToVec) {
    ComponentStore store;
    createCompVec<TestComponent>(store, 1);
    ASSERT_EQ(store.size(), 1);
    ASSERT_EQ(getCompVec<TestComponent>(store, 1).size(), 0);

    // Ensure that no new vectors are created
    auto compFullId = addComponent(store, TestComponent { true, 20 }, 1);
    ASSERT_EQ(store.size(), 1);

    // Ensure that the item is actually appended
    auto& vec = getCompVec<TestComponent>(store, 1);
    ASSERT_EQ(vec.size(), 1);
    ASSERT_EQ(vec.at(compFullId.second).height, 20);
}

TEST(TEST_SUITE, AsCompSet) {
    ComponentStore store;
    ASSERT_EQ(asCompSet(store).size(), 0);

    addComponent(store, TestComponent { true, 20 }, 1);
    addComponent(store, TestComponent { true, 20 }, 1);
    addComponent(store, TestComponent { true, 20 }, 1);
    addComponent(store, TestComponent { true, 20 }, 1);
    addComponent(store, TestComponent { true, 20 }, 2);
    addComponent(store, TestComponent { true, 20 }, 2);

    int group1Count = 0;
    int group2Count = 0;
    for (const auto& compFullId : asCompSet(store)) {
        if (compFullId.first == 1) {
            ++group1Count;
        } else if (compFullId.first == 2) {
            ++group2Count;
        }
    }

    ASSERT_EQ(group1Count, 4);
    ASSERT_EQ(group2Count, 2);
}

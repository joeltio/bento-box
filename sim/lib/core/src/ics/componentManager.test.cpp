#include <gtest/gtest.h>
#include <core/ics/component.h>
#include <core/ics/componentManager.h>

#define TEST_SUITE ComponentManagerTest

struct TestComponent : public ics::DefaultComponent {
    int length;
};

TEST(TEST_SUITE, AddComponent) {
    auto manager = ComponentManager();
    auto comp = TestComponent { true, 3 };
    // Add by reference
    size_t idx = manager.add(comp);
    // Add by rvalue
    manager.add(TestComponent { true, 4 });

    ics::Component auto retrievedComp = manager.at<TestComponent>(idx);
    ASSERT_EQ(retrievedComp.length, 3);
}

TEST(TEST_SUITE, AddAndRemoveComponent) {
    auto manager = ComponentManager();
    auto comp = TestComponent { true, 3 };
    size_t idx = manager.add(comp);

    manager.remove<TestComponent>(idx);
    EXPECT_THROW(
        manager.at<TestComponent>(idx),
        std::out_of_range
    );
}

TEST(TEST_SUITE, RetrieveByReference) {
    auto manager = ComponentManager();
    size_t idx = manager.add(TestComponent { true, 3 });

    ics::Component auto& compRef = manager.at<TestComponent>(idx);
    compRef.length = 10;

    ics::Component auto retrievedComp = manager.at<TestComponent>(idx);
    ASSERT_EQ(retrievedComp.isActive, true);
    ASSERT_EQ(retrievedComp.length, 10);
}

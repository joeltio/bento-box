#include <gtest/gtest.h>
#include "component.h"
#include "compVec.h"

#define TEST_SUITE CompVecTest

using namespace ics;

struct TestComp : public DefaultComponent {
    int height;
};

TEST(TEST_SUITE, StoreAndRetrieve) {
    auto vec = CompVec<TestComp>();
    vec.add(TestComp { true, 3 });

    TestComp value = vec.at(0);
    ASSERT_EQ(value.height, 3);
}

TEST(TEST_SUITE, RetrieveNonExistentComponent) {
    auto vec = CompVec<TestComp>();
    EXPECT_THROW(
        vec.at(0),
        std::out_of_range
    );
}

TEST(TEST_SUITE, ReuseDeletedComponent) {
    auto vec = CompVec<TestComp>();

    // Create two elements
    auto firstElementIdx = vec.add(TestComp{ true, 3 });
    vec.add(TestComp{ true, 3 });

    // Remove the first
    vec.remove(firstElementIdx);

    // The first element's memory location should be reused
    auto newElement = TestComp { true, 3 };
    auto newInsertIndex = vec.add(newElement);
    ASSERT_EQ(firstElementIdx, newInsertIndex);

    // The values should be the newly inserted component's values
    ics::Component auto firstElement = vec.at(firstElementIdx);
    ASSERT_EQ(firstElement, newElement);
    ASSERT_EQ(firstElement.height, 3);
}

TEST(TEST_SUITE, RetrieveDeletedComponent) {
    auto vec = CompVec<TestComp>();
    auto idx = vec.add(TestComp{ true, 3 });
    vec.remove(idx);
    EXPECT_THROW(
        vec.at(idx),
        std::out_of_range
    );
    EXPECT_THROW(
        vec[idx],
        std::out_of_range
    );
}

#include <gtest/gtest.h>
#include "component.h"
#include "compVec.h"

#define TEST_SUITE CompVecTest

using namespace ics;

struct ParentComp : public DefaultComponent {
    int height;
};

struct ChildComp : public ParentComp {
    int width;
};

TEST(TEST_SUITE, StoreAndRetrieve) {
    auto vec = CompVec<ChildComp>();
    vec.add(ChildComp { true, 1, 2 });

    ChildComp value = vec.at(0);
    ASSERT_EQ(value.height, 1);
    ASSERT_EQ(value.width, 2);
}

TEST(TEST_SUITE, RetrieveNonExistentComponent) {
    auto vec = CompVec<ChildComp>();
    EXPECT_THROW(
        vec.at(0),
        std::out_of_range
    );
}

TEST(TEST_SUITE, ReuseDeletedComponent) {
    auto vec = CompVec<ChildComp>();

    // Create two elements
    auto firstElementIdx = vec.add(ChildComp{true, 1, 2});
    vec.add(ChildComp{true, 1, 2});

    // Remove the first
    vec.remove(firstElementIdx);

    // The first element's memory location should be reused
    auto newElement = ChildComp { true, 3, 4 };
    auto newInsertIndex = vec.add(newElement);
    ASSERT_EQ(firstElementIdx, newInsertIndex);

    // The values should be the newly inserted component's values
    ics::Component auto firstElement = vec.at(firstElementIdx);
    ASSERT_EQ(firstElement, newElement);
    ASSERT_EQ(firstElement.height, 3);
    ASSERT_EQ(firstElement.width, 4);
}

TEST(TEST_SUITE, RetrieveDeletedComponent) {
    auto vec = CompVec<ChildComp>();
    auto idx = vec.add(ChildComp{true, 1, 2});
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

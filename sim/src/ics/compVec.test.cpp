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

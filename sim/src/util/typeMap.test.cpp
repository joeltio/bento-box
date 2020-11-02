#include "gtest/gtest.h"
#include "typeMap.h"

#define TEST_SUITE TypeMapTest

using namespace util;

struct Base {
    int x;
    bool operator==(const Base&) const = default;
};

struct Derived : public Base {
    int y;
};

TEST(TEST_SUITE, InsertAndRetrieveFromTypeMap) {
    auto map = TypeMap<Base>();
    auto d = Derived { 1, 2 };
    EXPECT_EQ(d.x, 1);
    EXPECT_EQ(d.y, 2);

    map.insert(d);

    EXPECT_EQ(map.at<Derived>(), d);
}

#include "gtest/gtest.h"
#include "typeMap.h"

#define TEST_SUITE TypeMapTest

using namespace util;

struct TestStruct {
    int x;
    bool operator==(const TestStruct&) const = default;
};

TEST(TEST_SUITE, InsertAndRetrieveFromTypeMap) {
    auto map = TypeMap();
    auto d = TestStruct { 1 };

    map.insert(d);

    EXPECT_EQ(map.at<TestStruct>(), d);
}

TEST(TEST_SUITE, RetrieveNonExistent) {
    auto map = TypeMap();
    EXPECT_THROW(
        map.at<TestStruct>(),
        std::out_of_range
    );
}

TEST(TEST_SUITE, CheckExistence) {
    auto map = TypeMap();
    EXPECT_FALSE(map.has<TestStruct>());

    auto d = TestStruct { 1 };
    map.insert(d);
    EXPECT_TRUE(map.has<TestStruct>());
}

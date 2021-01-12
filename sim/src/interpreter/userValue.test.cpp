#include <gtest/gtest.h>
#include <interpreter/userValue.h>

#define TEST_SUITE UserValueTest

using namespace interpreter;

TEST(TEST_SUITE, MultiDimArrayRetrieve) {
    std::vector<UserValue> arr;
    for (int64_t i = 0; i < 12; ++i) {
        arr.emplace_back(i);
    }

    auto multiDimArray = UserArray(arr, {3, 4});

    ASSERT_EQ(std::get<int64_t>(multiDimArray.at({0, 1})), 1);
    ASSERT_EQ(std::get<int64_t>(multiDimArray.at({2, 1})), 9);
    ASSERT_EQ(std::get<int64_t>(multiDimArray.at({1, 3})), 7);
}

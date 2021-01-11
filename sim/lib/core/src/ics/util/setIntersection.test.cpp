#include <gtest/gtest.h>
#include <string>
#include <core/ics/util/setIntersection.h>

#define TEST_SUITE SetIntersectionTest

using namespace util;

TEST(TEST_SUITE, IntersectWithEmptySet) {
    std::unordered_set<int> emptySet;
    std::unordered_set<int> otherSet = { 1, 2, 3 };

    ASSERT_EQ(setIntersection(emptySet, otherSet).size(), 0);
    ASSERT_EQ(setIntersection(otherSet, emptySet).size(), 0);
}

TEST(TEST_SUITE, IntersectWithSameSet) {
    std::unordered_set<int> set = { 1, 2, 3 };
    std::unordered_set<int> otherSet = { 1, 2, 3 };

    ASSERT_EQ(setIntersection(set, otherSet).size(), 3);
    ASSERT_EQ(setIntersection(otherSet, set).size(), 3);
}

TEST(TEST_SUITE, IntersectWithDifferentSets) {
    std::unordered_set<int> set = { 3, 8, 2 };
    std::unordered_set<int> otherSet = { 3, 9, 4 };

    // Assert size
    ASSERT_EQ(setIntersection(set, otherSet).size(), 1);
    ASSERT_EQ(setIntersection(otherSet, set).size(), 1);

    // Assert value
    auto firstElement = *setIntersection(set, otherSet).begin();
    ASSERT_EQ(firstElement, 3);
}

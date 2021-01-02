#include <gtest/gtest.h>
#include <core/systemContext.h>

#define TEST_SUITE Component

struct TestStructIndexStore {};

TEST(TEST_SUITE, IndexStoreAsStruct) {
    ASSERT_TRUE(IndexStore<TestStructIndexStore>);
}

TEST(TEST_SUITE, IndexStoreMustNotHaveNumericTemplate) {
    ASSERT_FALSE(IndexStore<int>);
    ASSERT_FALSE(IndexStore<double>);
    ASSERT_FALSE(IndexStore<char>);
    ASSERT_FALSE(IndexStore<bool>);
    ASSERT_FALSE(IndexStore<float>);
}
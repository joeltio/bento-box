#include <gtest/gtest.h>
#include <core/optics/lens.h>

#define TEST_SUITE Lenstest

using namespace optics;

TEST(TEST_SUITE, GetterFromLambda) {
    // From rvalue
    {
        auto getter = Getter<int, int, char>([](int j, int k) { return 'a'; });
        ASSERT_EQ(getter(5, 7), 'a');
    }

    // From lvalue
    {
        auto lambdaGetter = [](int j, int k) { return j + k; };
        auto getter = Getter<int, int, int>(lambdaGetter);
        ASSERT_EQ(getter(9, 10), 19);
    }
}

TEST(TEST_SUITE, ComposeGetters) {
    auto getter = Getter<int, int, int>([](int j, int k) { return j + k; });
    auto composedGetter = getter.compose<int>([](int h) { return h + 20; });

    ASSERT_EQ(composedGetter(1, 2), 23);
}

TEST(TEST_SUITE, PrecomposeGetters) {
    auto getter = Getter<int, int>([](int j) { return j * 10; });
    auto precomposedGetter =
        getter.precompose<int>([](int h) -> int { return h + 20; });

    ASSERT_EQ(precomposedGetter(1), 210);
}

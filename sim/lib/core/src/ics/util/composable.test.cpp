#include <core/ics/util/composable.h>
#include <gtest/gtest.h>

#include <string>

#define TEST_SUITE ComposableTest

using namespace util;

char f(int x) { return 'y'; }

bool g(char x) { return false; }

std::string h(bool x) { return "hello"; }

TEST(TEST_SUITE, ComposesFunctions) {
    auto val = Composable(3000) | &f | &g | &h;
    ASSERT_EQ(val.data, "hello");
}

typedef std::unordered_map<size_t, std::unique_ptr<int>> Store;
Store& j(Store& store) { return store; }

TEST(TEST_SUITE, ComposeByReference) {
    Store store;
    store.emplace(1, std::make_unique<int>(10));
    auto val = Composable<Store&>(store) | &j;
    ASSERT_EQ(*val.data.at(1), 10);
}

#include <gtest/gtest.h>
#include "component.h"

#define TEST_SUITE Component

using namespace ics;

template<Component T>
void DefaultComponentFulfillsConcept(T val) noexcept {}

TEST(TEST_SUITE, DefaultComponentFulfillsConcept) {
    auto x = DefaultComponent {};
    // Compilation will fail if DefaultComponent does not fulfill the concept
    DefaultComponentFulfillsConcept(x);
}

struct DerivedComp : public DefaultComponent {
    int height;
    char c;
};

TEST(TEST_SUITE, DerivedComponentsEquivalence) {
    auto d1 = DerivedComp {
        .height = 3,
        .c = 'c',
    };

    auto d2 = DerivedComp {
        .height = 3,
        .c = 'c',
    };

    auto d3 = d1;

    ASSERT_EQ(d1, d2);
    ASSERT_EQ(d3, d1);
}

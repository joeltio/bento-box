#include <gtest/gtest.h>
#include <core/ics/component.h>

#define TEST_SUITE Component

using namespace ics;

TEST(TEST_SUITE, DefaultComponentFulfillsConcept) {
    ASSERT_TRUE(Component<DefaultComponent>);
}

struct IncorrectNoIsactiveComponent {
    bool operator==(const IncorrectNoIsactiveComponent&) const = default;
};

TEST(TEST_SUITE, RequireIsactive) {
    ASSERT_FALSE(Component<IncorrectNoIsactiveComponent>);
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

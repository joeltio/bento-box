#include <gtest/gtest.h>
#include <core/ics/component.h>
#include <core/ics/index.h>

#define TEST_SUITE Index

using namespace ics;

class CorrectIndex {
public:
    template<Component C>
    void addComponent(C c) {};

    template<Component C>
    void removeComponent(C c) {};
};

TEST(TEST_SUITE, HasAddAndRemoveComponent) {
    ASSERT_TRUE(Index<CorrectIndex>);
}

class IncorrectUnconstrainedIndex {
public:
    template<typename C>
    void addComponent(C c) {};

    template<typename C>
    void removeComponent(C c) {};
};

TEST(TEST_SUITE, DISABLED_DisallowsUnconstrainedTypenames) {
    ASSERT_FALSE(Index<IncorrectUnconstrainedIndex>);
}

template<Component C>
class IncorrectNoTemplateMethodsIndex {
public:
    void addComponent(C c) {};

    void removeComponent(C c) {};
};

TEST(TEST_SUITE, DisallowsNonTemplateMethods) {
    ASSERT_FALSE(Index<IncorrectNoTemplateMethodsIndex<DefaultComponent>>);
}

#include <gtest/gtest.h>
#include "component.h"
#include "index.h"

#define TEST_SUITE Index

using namespace ics;

template<Index T>
void isIndex(T a) {}

class CorrectIndex {
public:
    template<Component C>
    void addComponent(C c) {};

    template<Component C>
    void removeComponent(C c) {};
};

TEST(TEST_SUITE, HasAddAndRemoveComponent) {
    auto x = CorrectIndex();
    isIndex(x);
}

class IncorrectUnconstrainedIndex {
public:
    template<typename C>
    void addComponent(C c) {};

    template<typename C>
    void removeComponent(C c) {};
};

// Requires manual testing, throws compilation error
// Last tested Nov 5 2020, 10:55pm
TEST(TEST_SUITE, DISABLED_DisallowsUnconstrainedTypenames) {
    // The type parameters should only allow components
    auto x = IncorrectUnconstrainedIndex();
    isIndex(x);
    FAIL();
    SUCCEED();
}

template<Component C>
class IncorrectNoTemplateMethodsIndex {
public:
    void addComponent(C c) {};

    void removeComponent(C c) {};
};

// Requires manual testing, throws compilation error
// Last tested Nov 5 2020, 10:55pm
TEST(TEST_SUITE, DisallowsNonTemplateMethods) {
//    // The methods should have type parameters
//    auto x = IncorrectNoTemplateMethodsIndex<DefaultComponent>();
//    isIndex(x);
//    FAIL();
    SUCCEED();
}

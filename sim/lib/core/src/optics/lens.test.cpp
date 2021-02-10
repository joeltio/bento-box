#include <gtest/gtest.h>
#include <core/optics/lens.hpp>

#define TEST_SUITE Lenstest

using namespace optics;

TEST(TEST_SUITE, GetterFromLambda) {
    // From rvalue
    {
        auto getter = Getter<char, int, int>([](int j, int k) { return 'a'; });
        ASSERT_EQ(getter.get(5, 7), 'a');
    }

    // From lvalue
    {
        auto lambdaGetter = []<class T, class U>(T&& j, U&& k) {
            return j + k;
        };
        auto getter = Getter<int, int, int>(lambdaGetter);
        // This is to test that get can accept an lvalue
        auto val = 9;
        ASSERT_EQ(getter.get(val, 10), 19);
    }
}

TEST(TEST_SUITE, ComposeGetters) {
    auto getter = Getter<int, int, int>([](int j, int k) { return j + k; });
    auto composedGetter = getter.compose<int>([](int h) { return h + 20; });

    ASSERT_EQ(composedGetter.get(1, 2), 23);
}

TEST(TEST_SUITE, PrecomposeGetters) {
    auto getter = Getter<int, int>([](int j) { return j * 10; });
    auto precomposedGetter =
        getter.precompose<int>([](int h) -> int { return h + 20; });

    ASSERT_EQ(precomposedGetter.get(1), 210);
}

TEST(TEST_SUITE, LensFromLambda) {
    // From rvalue
    {
        int storedVal = 3;
        auto lens =
            Lens<int, int>([](int&& j) -> int& { return j; },
                           [](int& j, int newVal) -> void { j = newVal - 10; });
        ASSERT_EQ(lens.get(3), 3);
        lens.set(14, storedVal);
        ASSERT_EQ(storedVal, 4);
    }

    // From lvalue
    {
        int storedVal = 3;
        auto getter = [](int&& j, int&& k) -> int& { return j; };
        auto setter = [](int& j, int newVal) { j = newVal - 10; };
        auto lens = Lens<int, int, int>(getter, setter);
        // This is to test that get can accept an lvalue
        ASSERT_EQ(lens.get(storedVal, 10), 3);
        lens.set(14, storedVal, 5);
        ASSERT_EQ(storedVal, 4);
    }
}

struct B {
    int height = 0;
};

struct A {
    B b;
};

TEST(TEST_SUITE, ComposeLens) {
    auto storedVal = A{B{10}};
    auto getter = [](A&& a) -> B& { return a.b; };
    auto setter = [](B& b, B&& newB) { b = newB; };
    auto lens = Lens<B, A>(getter, setter);

    ASSERT_EQ(lens.get(storedVal).height, 10);

    auto getterComp = [](B&& b) -> int& { return b.height; };
    auto setterComp = [](int& height, int&& newHeight) { height = newHeight; };
    auto lensComp = Lens<int, B>(getterComp, setterComp);

    auto composedLens = lens.compose(lensComp);
    ASSERT_EQ(composedLens.get(storedVal), 10);
    composedLens.set(20, storedVal);
    ASSERT_EQ(composedLens.get(storedVal), 20);
}

TEST(TEST_SUITE, PrecomposeLens) {
    auto storedVal = A{B{10}};
    auto getter = [](A&& a) -> B& { return a.b; };
    auto setter = [](B& b, B&& newB) { b = newB; };
    auto lens = Lens<B, A>(getter, setter);

    ASSERT_EQ(lens.get(storedVal).height, 10);

    auto getterComp = [](B&& b) -> int& { return b.height; };
    auto setterComp = [](int& height, int&& newHeight) { height = newHeight; };
    auto lensComp = Lens<int, B>(getterComp, setterComp);

    auto composedLens = lensComp.precompose(lens);
    ASSERT_EQ(composedLens.get(storedVal), 10);
    composedLens.set(20, storedVal);
    ASSERT_EQ(composedLens.get(storedVal), 20);
}

TEST(TEST_SUITE, CompositionCopiesLenses) {
    // Create the lenses
    auto getter = [](A&& a) -> B& { return a.b; };
    auto setter = [](B& b, B&& newB) { b = newB; };
    auto lensAPtr = new Lens<B, A>(getter, setter);

    auto getterComp = [](B&& b) -> int& { return b.height; };
    auto setterComp = [](int& height, int&& newHeight) { height = newHeight; };
    auto lensBPtr = new Lens<int, B>(getterComp, setterComp);

    auto composedLens = lensAPtr->compose(*lensBPtr);

    // Delete the lenses
    delete lensAPtr;
    lensAPtr = nullptr;
    delete lensBPtr;
    lensBPtr = nullptr;

    // Use the composed lens
    auto storedVal = A{B{10}};
    ASSERT_EQ(composedLens.get(storedVal), 10);
    auto j = 20;
    composedLens.set(j, storedVal);
    ASSERT_EQ(composedLens.get(storedVal), 20);
}

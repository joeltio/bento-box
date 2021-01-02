#include <gtest/gtest.h>
#include <any>
#include <core/ics/component.h>
#include <core/ics/compVec.h>

#define TEST_SUITE CompVecTest

using namespace ics;

struct TestComp : public BaseComponent {
    int height;
};

TEST(TEST_SUITE, StoreAndRetrieve) {
    auto vec = CompVec<TestComp>();
    auto id = vec.add(TestComp { true, 3 });

    TestComp value = vec.at(id);
    ASSERT_EQ(value.height, 3);
}

TEST(TEST_SUITE, RetrieveNonExistentComponent) {
    auto vec = CompVec<TestComp>();
    EXPECT_THROW(
        vec.at(0),
        std::out_of_range
    );
}

TEST(TEST_SUITE, RetrieveDeletedComponent) {
    auto vec = CompVec<TestComp>();
    auto id = vec.add(TestComp{ true, 3 });
    vec.remove(id);
    EXPECT_THROW(
        vec.at(id),
        std::out_of_range
    );
    EXPECT_THROW(
        vec[id],
        std::out_of_range
    );
}

TEST(TEST_SUITE, RetrieveByReference) {
    auto vec = CompVec<TestComp>();

    {
        auto idx = vec.add(TestComp{true, 3});

        TestComp &comp = vec.at(idx);
        comp.height = 2;

        ics::Component auto vecComp = vec.at(idx);
        ASSERT_EQ(vecComp.height, 2);
    }

    {
        auto idx = vec.add(TestComp{true, 3});

        TestComp &comp = vec[idx];
        comp.height = 2;

        ics::Component auto vecComp = vec.at(idx);
        ASSERT_EQ(vecComp.height, 2);
    }
}

TEST(TEST_SUITE, StoreAsUnknownAndRetrieve) {
    auto vec = CompVec<TestComp>();
    auto trueCompId = vec.add(TestComp { true, 3 });
    auto falseCompId = vec.add(TestComp { false, 3 });
    vec.add(TestComp { true, 3 });
    CompVec<TestComp>* vecPtr = &vec;

    auto storedVec = reinterpret_cast<CompVec<BaseComponent>*>(vecPtr);

    ASSERT_EQ(storedVec->size(), 3);
    ASSERT_TRUE(storedVec->at(trueCompId).isActive);
    EXPECT_THROW(storedVec->at(falseCompId), std::out_of_range);
}

#include <gtest/gtest.h>
#include <interpreter/userValue.h>

#include <utility>

#define TEST_SUITE UserValueTest

using namespace interpreter;

TEST(TEST_SUITE, SetValue) {
    auto val = bento::protos::Value();
    // Integral types
    setVal(val, 3);
    ASSERT_EQ(val.primitive().value_case(),
              bento::protos::Value_Primitive::kInt32);
    ASSERT_EQ(val.primitive().int_32(), 3);
    setVal(val, 3L);
    ASSERT_EQ(val.primitive().value_case(),
              bento::protos::Value_Primitive::kInt64);
    ASSERT_EQ(val.primitive().int_64(), 3L);

    // Floating point types
    setVal(val, 3.0f);
    ASSERT_EQ(val.primitive().value_case(),
              bento::protos::Value_Primitive::kFloat32);
    ASSERT_EQ(val.primitive().float_32(), 3.0f);
    setVal(val, 3.0);
    ASSERT_EQ(val.primitive().value_case(),
              bento::protos::Value_Primitive::kFloat64);
    ASSERT_EQ(val.primitive().float_64(), 3.0);

    // Other types
    setVal(val, "hello!");
    ASSERT_EQ(val.primitive().value_case(),
              bento::protos::Value_Primitive::kStrVal);
    ASSERT_EQ(val.primitive().str_val(), "hello!");
    setVal(val, true);
    ASSERT_EQ(val.primitive().value_case(),
              bento::protos::Value_Primitive::kBoolean);
    ASSERT_EQ(val.primitive().boolean(), true);
}

TEST(TEST_SUITE, GetValue) {
    auto val = bento::protos::Value();
    val.mutable_primitive()->set_int_32(10);
    ASSERT_EQ(getVal<proto_INT32>(val), 10);
    val.mutable_primitive()->set_int_64(20);
    ASSERT_EQ(getVal<proto_INT64>(val), 20);

    val.mutable_primitive()->set_float_32(30.0f);
    ASSERT_FLOAT_EQ(getVal<proto_FLOAT32>(val), 30.0f);
    val.mutable_primitive()->set_float_64(40.0);
    ASSERT_FLOAT_EQ(getVal<proto_FLOAT64>(val), 40.0f);

    val.mutable_primitive()->set_str_val("hello");
    ASSERT_EQ(getVal<proto_STR>(val), "hello");
    val.mutable_primitive()->set_boolean(true);
    ASSERT_EQ(getVal<proto_BOOL>(val), true);
}

TEST(TEST_SUITE, ConvertTypeFromLambda) {
    auto add = []<class X, class Y>(X x, Y y) { return x + y; };

    // Int32 with int64
    {
        proto_INT32 x = 3;
        proto_INT64 y = 20;

        auto val = bento::protos::Value();
        setVal(val, add(x, y));
        ASSERT_EQ(val.primitive().value_case(),
                  bento::protos::Type_Primitive_INT64);
    }

    // float32 with int32
    {
        proto_FLOAT32 x = 3.0;
        proto_INT32 y = 20;

        auto val = bento::protos::Value();
        setVal(val, add(x, y));
        ASSERT_EQ(val.primitive().value_case(),
                  bento::protos::Type_Primitive_FLOAT32);
    }

    // float64 with int32
    {
        proto_FLOAT64 x = 3.0;
        proto_INT32 y = 20;

        auto val = bento::protos::Value();
        setVal(val, add(x, y));
        ASSERT_EQ(val.primitive().value_case(),
                  bento::protos::Type_Primitive_FLOAT64);
    }
}

TEST(TEST_SUITE, RetTypeFromAdditionType) {
    auto max = []<class X, class Y>(X x, Y y) {
        typedef decltype(std::declval<X>() + std::declval<Y>()) RetType;
        if (x > y) {
            return (RetType)x;
        } else {
            return (RetType)y;
        }
    };

    // float64 with int32
    {
        proto_FLOAT64 x = 3.0;
        proto_INT32 y = 20;

        auto val = bento::protos::Value();
        setVal(val, max(x, y));
        ASSERT_EQ(val.primitive().value_case(),
                  bento::protos::Type_Primitive_FLOAT64);
    }
}

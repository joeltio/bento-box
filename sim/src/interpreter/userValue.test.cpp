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

TEST(TEST_SUITE, IsValueOfType) {
    auto val = bento::protos::Value();
    // Test all the true cases
    val.mutable_primitive()->set_int_32(10);
    ASSERT_TRUE(isValOfType<proto_INT32>(val));
    val.mutable_primitive()->set_int_64(20);
    ASSERT_TRUE(isValOfType<proto_INT64>(val));

    val.mutable_primitive()->set_float_32(30.0f);
    ASSERT_TRUE(isValOfType<proto_FLOAT32>(val));
    val.mutable_primitive()->set_float_64(40.0);
    ASSERT_TRUE(isValOfType<proto_FLOAT64>(val));

    val.mutable_primitive()->set_str_val("hello");
    ASSERT_TRUE(isValOfType<proto_STR>(val));
    val.mutable_primitive()->set_boolean(true);
    ASSERT_TRUE(isValOfType<proto_BOOL>(val));

    // Test some false cases
    ASSERT_FALSE(isValOfType<proto_INT32>(val));
    ASSERT_FALSE(isValOfType<proto_INT64>(val));

    val.mutable_primitive()->set_float_32(30.0f);
    ASSERT_FALSE(isValOfType<proto_STR>(val));
    ASSERT_FALSE(isValOfType<proto_FLOAT64>(val));

    val.mutable_primitive()->set_int_32(30);
    ASSERT_FALSE(isValOfType<proto_BOOL>(val));
    ASSERT_FALSE(isValOfType<proto_FLOAT32>(val));
}

TEST(TEST_SUITE, IsValueOfTypes) {
    auto val = bento::protos::Value();

    val.mutable_primitive()->set_int_32(10);
    bool isValid = isValOfTypes<proto_INT32, proto_FLOAT64>(val);
    // For some reason, putting the literal into the ASSERT_TRUE macro fails to
    // compile
    ASSERT_TRUE(isValid);
    isValid = isValOfTypes<proto_FLOAT64, proto_STR, proto_BOOL>(val);
    ASSERT_FALSE(isValid);

    val.mutable_primitive()->set_boolean(true);
    isValid = isValOfTypes<proto_STR, proto_FLOAT64, proto_BOOL>(val);
    ASSERT_TRUE(isValid);
    isValid = isValOfTypes<proto_FLOAT64, proto_STR, proto_INT32>(val);
    ASSERT_FALSE(isValid);
}

TEST(TEST_SUITE, RunFnWithValRunsFunction) {
    {
        auto val = bento::protos::Value();
        val.mutable_primitive()->set_int_32(10);

        auto newVal =
            runFnWithVal<proto_INT32>(val, []<class X>(X x) { return x + 3; });
        ASSERT_EQ(newVal.primitive().int_32(), 13);
    }
    {
        auto valX = bento::protos::Value();
        valX.mutable_primitive()->set_float_32(10.0f);
        auto valY = bento::protos::Value();
        valY.mutable_primitive()->set_float_32(20.0f);

        auto newVal = runFnWithVal<proto_FLOAT32>(
            valX, valY, []<class X, class Y>(X x, Y y) { return x + y; });
        ASSERT_FLOAT_EQ(newVal.primitive().float_32(), 30.0f);
    }
}

TEST(TEST_SUITE, RunFnWithValDetectsTypes) {
    auto valFloat = bento::protos::Value();
    valFloat.mutable_primitive()->set_float_32(10.0f);

    auto valInt = bento::protos::Value();
    valInt.mutable_primitive()->set_int_32(20);

    auto newVal = runFnWithVal<proto_FLOAT32, proto_INT32>(
        valFloat, valInt, []<class X, class Y>(X x, Y y) { return x + y; });
    // The addition of float and int is float
    ASSERT_FLOAT_EQ(newVal.primitive().float_32(), 30.0);
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

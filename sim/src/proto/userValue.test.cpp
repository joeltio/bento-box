#include <gtest/gtest.h>
#include <proto/userValue.h>
#include <bento/protos/types.pb.h>

#include <utility>

#define TEST_SUITE UserValueTest

using namespace proto;

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
    ASSERT_EQ(getVal<INT32>(val), 10);
    val.mutable_primitive()->set_int_64(20);
    ASSERT_EQ(getVal<INT64>(val), 20);

    val.mutable_primitive()->set_float_32(30.0f);
    ASSERT_FLOAT_EQ(getVal<FLOAT32>(val), 30.0f);
    val.mutable_primitive()->set_float_64(40.0);
    ASSERT_FLOAT_EQ(getVal<FLOAT64>(val), 40.0f);

    val.mutable_primitive()->set_str_val("hello");
    ASSERT_EQ(getVal<STR>(val), "hello");
    val.mutable_primitive()->set_boolean(true);
    ASSERT_EQ(getVal<BOOL>(val), true);
}

TEST(TEST_SUITE, IsValueOfType) {
    auto val = bento::protos::Value();
    // Test all the true cases
    val.mutable_primitive()->set_int_32(10);
    ASSERT_TRUE(isValOfType<INT32>(val));
    val.mutable_primitive()->set_int_64(20);
    ASSERT_TRUE(isValOfType<INT64>(val));

    val.mutable_primitive()->set_float_32(30.0f);
    ASSERT_TRUE(isValOfType<FLOAT32>(val));
    val.mutable_primitive()->set_float_64(40.0);
    ASSERT_TRUE(isValOfType<FLOAT64>(val));

    val.mutable_primitive()->set_str_val("hello");
    ASSERT_TRUE(isValOfType<STR>(val));
    val.mutable_primitive()->set_boolean(true);
    ASSERT_TRUE(isValOfType<BOOL>(val));

    // Test some false cases
    ASSERT_FALSE(isValOfType<INT32>(val));
    ASSERT_FALSE(isValOfType<INT64>(val));

    val.mutable_primitive()->set_float_32(30.0f);
    ASSERT_FALSE(isValOfType<STR>(val));
    ASSERT_FALSE(isValOfType<FLOAT64>(val));

    val.mutable_primitive()->set_int_32(30);
    ASSERT_FALSE(isValOfType<BOOL>(val));
    ASSERT_FALSE(isValOfType<FLOAT32>(val));
}

TEST(TEST_SUITE, IsValueOfTypes) {
    auto val = bento::protos::Value();

    val.mutable_primitive()->set_int_32(10);
    bool isValid = isValOfTypes<INT32, FLOAT64>(val);
    // For some reason, putting the literal into the ASSERT_TRUE macro fails to
    // compile
    ASSERT_TRUE(isValid);
    isValid = isValOfTypes<FLOAT64, STR, BOOL>(val);
    ASSERT_FALSE(isValid);

    val.mutable_primitive()->set_boolean(true);
    isValid = isValOfTypes<STR, FLOAT64, BOOL>(val);
    ASSERT_TRUE(isValid);
    isValid = isValOfTypes<FLOAT64, STR, INT32>(val);
    ASSERT_FALSE(isValid);
}

TEST(TEST_SUITE, IsTypeOfType) {
    auto type = bento::protos::Type();
    // Test all the true cases
    type.set_primitive(bento::protos::Type_Primitive_INT32);
    ASSERT_TRUE(isTypeOfType<INT32>(type));
    type.set_primitive(bento::protos::Type_Primitive_INT64);
    ASSERT_TRUE(isTypeOfType<INT64>(type));

    type.set_primitive(bento::protos::Type_Primitive_FLOAT32);
    ASSERT_TRUE(isTypeOfType<FLOAT32>(type));
    type.set_primitive(bento::protos::Type_Primitive_FLOAT64);
    ASSERT_TRUE(isTypeOfType<FLOAT64>(type));

    type.set_primitive(bento::protos::Type_Primitive_STRING);
    ASSERT_TRUE(isTypeOfType<STR>(type));
    type.set_primitive(bento::protos::Type_Primitive_BOOL);
    ASSERT_TRUE(isTypeOfType<BOOL>(type));

    // Test some false cases
    ASSERT_FALSE(isTypeOfType<INT32>(type));
    ASSERT_FALSE(isTypeOfType<INT64>(type));

    type.set_primitive(bento::protos::Type_Primitive_FLOAT32);
    ASSERT_FALSE(isTypeOfType<STR>(type));
    ASSERT_FALSE(isTypeOfType<FLOAT64>(type));

    type.set_primitive(bento::protos::Type_Primitive_INT32);
    ASSERT_FALSE(isTypeOfType<BOOL>(type));
    ASSERT_FALSE(isTypeOfType<FLOAT32>(type));
}

TEST(TEST_SUITE, IsTypeOfTypes) {
    auto type = bento::protos::Type();

    type.set_primitive(bento::protos::Type_Primitive_INT32);
    bool isValid = isTypeOfTypes<INT32, FLOAT64>(type);
    // For some reason, putting the literal into the ASSERT_TRUE macro fails to
    // compile
    ASSERT_TRUE(isValid);
    isValid = isTypeOfTypes<FLOAT64, STR, BOOL>(type);
    ASSERT_FALSE(isValid);

    type.set_primitive(bento::protos::Type_Primitive_BOOL);
    isValid = isTypeOfTypes<STR, FLOAT64, BOOL>(type);
    ASSERT_TRUE(isValid);
    isValid = isTypeOfTypes<FLOAT64, STR, INT32>(type);
    ASSERT_FALSE(isValid);
}

TEST(TEST_SUITE, RunFnWithValRunsFunction) {
    {
        auto val = bento::protos::Value();
        val.mutable_primitive()->set_int_32(10);

        auto newVal =
            runFnWithVal<INT32>(val, []<class X>(X x) { return x + 3; });
        ASSERT_EQ(newVal.primitive().int_32(), 13);
    }
    {
        auto valX = bento::protos::Value();
        valX.mutable_primitive()->set_float_32(10.0f);
        auto valY = bento::protos::Value();
        valY.mutable_primitive()->set_float_32(20.0f);

        auto newVal = runFnWithVal<FLOAT32>(
            valX, valY, []<class X, class Y>(X x, Y y) { return x + y; });
        ASSERT_FLOAT_EQ(newVal.primitive().float_32(), 30.0f);
    }
}

TEST(TEST_SUITE, RunFnWithValDetectsTypes) {
    auto valFloat = bento::protos::Value();
    valFloat.mutable_primitive()->set_float_32(10.0f);

    auto valInt = bento::protos::Value();
    valInt.mutable_primitive()->set_int_32(20);

    auto newVal = runFnWithVal<FLOAT32, INT32>(
        valFloat, valInt, []<class X, class Y>(X x, Y y) { return x + y; });
    // The addition of float and int is float
    ASSERT_FLOAT_EQ(newVal.primitive().float_32(), 30.0);
}

TEST(TEST_SUITE, RunFnWithValTypeDetectsTypes) {
    auto typeFloat = bento::protos::Type();
    typeFloat.set_primitive(bento::protos::Type_Primitive_FLOAT32);

    auto valid = false;
    runFnWithValType<FLOAT32, INT32>(typeFloat, [&valid]<class X>(X* _) {
        valid = std::is_same_v<X, FLOAT32>;
    });
    ASSERT_TRUE(valid);

    auto typeInt = bento::protos::Type();
    typeInt.set_primitive(bento::protos::Type_Primitive_INT32);

    valid = false;
    runFnWithValType<FLOAT32, INT32>(
        typeInt, [&valid]<class X>(X* _) { valid = std::is_same_v<X, INT32>; });
    ASSERT_TRUE(valid);
}

TEST(TEST_SUITE, ConvertTypeFromLambda) {
    auto add = []<class X, class Y>(X x, Y y) { return x + y; };

    // Int32 with int64
    {
        INT32 x = 3;
        INT64 y = 20;

        auto val = bento::protos::Value();
        setVal(val, add(x, y));
        ASSERT_EQ(val.primitive().value_case(),
                  bento::protos::Type_Primitive_INT64);
    }

    // float32 with int32
    {
        FLOAT32 x = 3.0;
        INT32 y = 20;

        auto val = bento::protos::Value();
        setVal(val, add(x, y));
        ASSERT_EQ(val.primitive().value_case(),
                  bento::protos::Type_Primitive_FLOAT32);
    }

    // float64 with int32
    {
        FLOAT64 x = 3.0;
        INT32 y = 20;

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
        FLOAT64 x = 3.0;
        INT32 y = 20;

        auto val = bento::protos::Value();
        setVal(val, max(x, y));
        ASSERT_EQ(val.primitive().value_case(),
                  bento::protos::Type_Primitive_FLOAT64);
    }
}

TEST(TEST_SUITE, ValHasCorrectDataType) {
    bento::protos::Value val;
    val.mutable_primitive()->set_int_64(3);

    // No data type
    ASSERT_FALSE(valHasCorrectDataType(val));

    // Mismatched
    val.mutable_data_type()->set_primitive(bento::protos::Type_Primitive_BOOL);
    ASSERT_FALSE(valHasCorrectDataType(val));

    // Correct data type
    val.mutable_data_type()->set_primitive(bento::protos::Type_Primitive_INT64);
    ASSERT_TRUE(valHasCorrectDataType(val));
}

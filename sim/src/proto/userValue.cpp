#include <proto/userValue.h>

namespace proto {
// Overloads for setting a value
void setVal(bento::protos::Value& protoVal, INT32 int32Val) {
    protoVal.mutable_data_type()->set_primitive(
        bento::protos::Type_Primitive_INT32);
    protoVal.mutable_primitive()->set_int_32(int32Val);
}

void setVal(bento::protos::Value& protoVal, INT64 int64Val) {
    protoVal.mutable_data_type()->set_primitive(
        bento::protos::Type_Primitive_INT64);
    protoVal.mutable_primitive()->set_int_64(int64Val);
}

void setVal(bento::protos::Value& protoVal, FLOAT32 float32Val) {
    protoVal.mutable_data_type()->set_primitive(
        bento::protos::Type_Primitive_FLOAT32);
    protoVal.mutable_primitive()->set_float_32(float32Val);
}

void setVal(bento::protos::Value& protoVal, FLOAT64 float64Val) {
    protoVal.mutable_data_type()->set_primitive(
        bento::protos::Type_Primitive_FLOAT64);
    protoVal.mutable_primitive()->set_float_64(float64Val);
}

void setVal(bento::protos::Value& protoVal, const std::string& strVal) {
    protoVal.mutable_primitive()->set_str_val(strVal);
    protoVal.mutable_data_type()->set_primitive(
        bento::protos::Type_Primitive_STRING);
}

void setVal(bento::protos::Value& protoVal, const char* strVal) {
    protoVal.mutable_primitive()->set_str_val(strVal);
    protoVal.mutable_data_type()->set_primitive(
        bento::protos::Type_Primitive_STRING);
}

void setVal(bento::protos::Value& protoVal, BOOL boolVal) {
    protoVal.mutable_data_type()->set_primitive(
        bento::protos::Type_Primitive_BOOL);
    protoVal.mutable_primitive()->set_boolean(boolVal);
}

template <>
INT32 getVal(const bento::protos::Value& protoVal) {
    return protoVal.primitive().int_32();
}

template <>
INT64 getVal(const bento::protos::Value& protoVal) {
    return protoVal.primitive().int_64();
}

template <>
FLOAT32 getVal(const bento::protos::Value& protoVal) {
    return protoVal.primitive().float_32();
}

template <>
FLOAT64 getVal(const bento::protos::Value& protoVal) {
    return protoVal.primitive().float_64();
}

template <>
STR getVal(const bento::protos::Value& protoVal) {
    return protoVal.primitive().str_val();
}

template <>
BOOL getVal(const bento::protos::Value& protoVal) {
    return protoVal.primitive().boolean();
}

template <>
bool isValOfType<INT32>(const bento::protos::Value& protoVal) {
    return protoVal.primitive().value_case() ==
           bento::protos::Value_Primitive::kInt32;
}

template <>
bool isValOfType<INT64>(const bento::protos::Value& protoVal) {
    return protoVal.primitive().value_case() ==
           bento::protos::Value_Primitive::kInt64;
}

template <>
bool isValOfType<FLOAT32>(const bento::protos::Value& protoVal) {
    return protoVal.primitive().value_case() ==
           bento::protos::Value_Primitive::kFloat32;
}

template <>
bool isValOfType<FLOAT64>(const bento::protos::Value& protoVal) {
    return protoVal.primitive().value_case() ==
           bento::protos::Value_Primitive::kFloat64;
}

template <>
bool isValOfType<STR>(const bento::protos::Value& protoVal) {
    return protoVal.primitive().value_case() ==
           bento::protos::Value_Primitive::kStrVal;
}

template <>
bool isValOfType<BOOL>(const bento::protos::Value& protoVal) {
    return protoVal.primitive().value_case() ==
           bento::protos::Value_Primitive::kBoolean;
}

template <>
bool isProtoTypeOfType<INT32>(const bento::protos::Type& protoType) {
    return protoType.primitive() == bento::protos::Type_Primitive_INT32;
}

template <>
bool isProtoTypeOfType<INT64>(const bento::protos::Type& protoType) {
    return protoType.primitive() == bento::protos::Type_Primitive_INT64;
}

template <>
bool isProtoTypeOfType<FLOAT32>(const bento::protos::Type& protoType) {
    return protoType.primitive() == bento::protos::Type_Primitive_FLOAT32;
}

template <>
bool isProtoTypeOfType<FLOAT64>(const bento::protos::Type& protoType) {
    return protoType.primitive() == bento::protos::Type_Primitive_FLOAT64;
}

template <>
bool isProtoTypeOfType<STR>(const bento::protos::Type& protoType) {
    return protoType.primitive() == bento::protos::Type_Primitive_STRING;
}

template <>
bool isProtoTypeOfType<BOOL>(const bento::protos::Type& protoType) {
    return protoType.primitive() == bento::protos::Type_Primitive_BOOL;
}

bool valHasCorrectDataType(const bento::protos::Value& val) {
    // Handle unset data_type
    if (!val.has_data_type()) {
        return false;
    }

    bool result;
    runFnWithValType<proto_ANY>(
        val.data_type(), [&val, &result]<class X>(X* _) {
            runFnWithVal<proto_ANY>(val, [&result]<class Y>(Y y) {
                result = std::is_same_v<X, Y>;
                // Return something random since it is required
                return 3;
            });
        });

    return result;
}

}  // namespace proto
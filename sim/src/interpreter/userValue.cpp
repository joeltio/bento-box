#include <interpreter/userValue.h>

namespace interpreter {
// Overloads for setting a value
void setVal(bento::protos::Value& protoVal, proto_INT32 int32Val) {
    protoVal.mutable_data_type()->set_primitive(
        bento::protos::Type_Primitive_INT32);
    protoVal.mutable_primitive()->set_int_32(int32Val);
}

void setVal(bento::protos::Value& protoVal, proto_INT64 int64Val) {
    protoVal.mutable_data_type()->set_primitive(
        bento::protos::Type_Primitive_INT64);
    protoVal.mutable_primitive()->set_int_64(int64Val);
}

void setVal(bento::protos::Value& protoVal, proto_FLOAT32 float32Val) {
    protoVal.mutable_data_type()->set_primitive(
        bento::protos::Type_Primitive_FLOAT32);
    protoVal.mutable_primitive()->set_float_32(float32Val);
}

void setVal(bento::protos::Value& protoVal, proto_FLOAT64 float64Val) {
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

void setVal(bento::protos::Value& protoVal, proto_BOOL boolVal) {
    protoVal.mutable_data_type()->set_primitive(
        bento::protos::Type_Primitive_BOOL);
    protoVal.mutable_primitive()->set_boolean(boolVal);
}

template <>
proto_INT32 getVal(bento::protos::Value& protoVal) {
    return protoVal.primitive().int_32();
}

template <>
proto_INT64 getVal(bento::protos::Value& protoVal) {
    return protoVal.primitive().int_64();
}

template <>
proto_FLOAT32 getVal(bento::protos::Value& protoVal) {
    return protoVal.primitive().float_32();
}

template <>
proto_FLOAT64 getVal(bento::protos::Value& protoVal) {
    return protoVal.primitive().float_64();
}

template <>
proto_STR getVal(bento::protos::Value& protoVal) {
    return protoVal.primitive().str_val();
}

template <>
proto_BOOL getVal(bento::protos::Value& protoVal) {
    return protoVal.primitive().boolean();
}

template <>
bool isValOfType<proto_INT32>(const bento::protos::Value& protoVal) {
    return protoVal.primitive().value_case() ==
           bento::protos::Value_Primitive::kInt32;
}

template <>
bool isValOfType<proto_INT64>(const bento::protos::Value& protoVal) {
    return protoVal.primitive().value_case() ==
           bento::protos::Value_Primitive::kInt64;
}

template <>
bool isValOfType<proto_FLOAT32>(const bento::protos::Value& protoVal) {
    return protoVal.primitive().value_case() ==
           bento::protos::Value_Primitive::kFloat32;
}

template <>
bool isValOfType<proto_FLOAT64>(const bento::protos::Value& protoVal) {
    return protoVal.primitive().value_case() ==
           bento::protos::Value_Primitive::kFloat64;
}

template <>
bool isValOfType<proto_STR>(const bento::protos::Value& protoVal) {
    return protoVal.primitive().value_case() ==
           bento::protos::Value_Primitive::kStrVal;
}

template <>
bool isValOfType<proto_BOOL>(const bento::protos::Value& protoVal) {
    return protoVal.primitive().value_case() ==
           bento::protos::Value_Primitive::kBoolean;
}

}  // namespace interpreter
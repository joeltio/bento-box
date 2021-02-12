#ifndef BENTOBOX_USERVALUE_H
#define BENTOBOX_USERVALUE_H

#include <type_traits>
#include <string>
#include <bento/protos/values.pb.h>

namespace interpreter {

// Type aliases for all the protobuf types
typedef int32_t proto_INT32;
typedef int64_t proto_INT64;
static_assert(CHAR_BIT * sizeof(float) == 32);
typedef float proto_FLOAT32;
static_assert(CHAR_BIT * sizeof(double) == 64);
typedef double proto_FLOAT64;
typedef std::string proto_STR;
typedef bool proto_BOOL;

// Concept to assert that the given type is a protobuf type
template <class T>
concept ProtobufType =
    std::is_same_v<T, proto_INT32> || std::is_same_v<T, proto_INT64> ||
    std::is_same_v<T, proto_FLOAT32> || std::is_same_v<T, proto_FLOAT64> ||
    std::is_same_v<T, proto_STR> || std::is_same_v<T, proto_BOOL>;

// Overloads for setting a value
void setVal(bento::protos::Value& protoVal, proto_INT32 int32Val);
void setVal(bento::protos::Value& protoVal, proto_INT64 int64Val);
void setVal(bento::protos::Value& protoVal, proto_FLOAT32 float32Val);
void setVal(bento::protos::Value& protoVal, proto_FLOAT64 float64Val);
void setVal(bento::protos::Value& protoVal, const std::string& strVal);
void setVal(bento::protos::Value& protoVal, const char* strVal);
void setVal(bento::protos::Value& protoVal, proto_BOOL boolVal);

// Get value
template <class T>
// Ensure that the values are protobuf values
requires ProtobufType<T> T getVal(bento::protos::Value& protoVal) {
    throw std::runtime_error("Invalid protobuf type.");
}

// Check value type
template <class T>
// Ensure that the values are protobuf values
requires ProtobufType<T> bool isValOfType(bento::protos::Value& protoVal) {
    throw std::runtime_error("Invalid protobuf type.");
}

}  // namespace interpreter

#endif  // BENTOBOX_USERVALUE_H

#ifndef BENTOBOX_VALUETYPE_H
#define BENTOBOX_VALUETYPE_H

#include <string>
#include <bento/protos/values.pb.h>

namespace proto {

// Returns a name for what the Value stores
std::string valStoredTypeName(const bento::protos::Value_Primitive& val);
std::string valStoredTypeName(const bento::protos::Value_Array& val);
std::string valStoredTypeName(const bento::protos::Value& val);

// Returns a name for what the Value says it stores under its data_type
std::string valDataTypeName(const bento::protos::Type_Primitive& valType);
std::string valDataTypeName(const bento::protos::Type_Array& valType);
std::string valDataTypeName(const bento::protos::Type& valType);

}  // namespace proto

#endif  // BENTOBOX_VALUETYPE_H

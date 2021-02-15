#ifndef BENTOBOX_USERVALUE_H
#define BENTOBOX_USERVALUE_H

#include <bento/protos/values.pb.h>

// Returns a name for what the Value stores
std::string valStoredTypeName(const bento::protos::Value_Primitive& val);
std::string valStoredTypeName(const bento::protos::Value_Array& val);
std::string valStoredTypeName(const bento::protos::Value& val);

// Returns a name for what the Value says it stores under its data_type
std::string valDataTypeName(const bento::protos::Type_Primitive& valType);
std::string valDataTypeName(const bento::protos::Type_Array& valType);
std::string valDataTypeName(const bento::protos::Type& valType);

#endif  // BENTOBOX_USERVALUE_H

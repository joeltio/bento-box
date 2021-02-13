#include <proto/valueType.h>

namespace proto {

std::string valStoredTypeName(const bento::protos::Value_Primitive& val) {
    std::string name = "Primitive[";
    switch (val.value_case()) {
        case bento::protos::Value_Primitive::kInt8:
            name += "8-bit Integer";
            break;
        case bento::protos::Value_Primitive::kInt32:
            name += "32-bit Integer";
            break;
        case bento::protos::Value_Primitive::kInt64:
            name += "64-bit Integer";
            break;
        case bento::protos::Value_Primitive::kFloat32:
            name += "32-bit Float";
            break;
        case bento::protos::Value_Primitive::kFloat64:
            name += "64-bit Float";
            break;
        case bento::protos::Value_Primitive::kStrVal:
            name += "String";
            break;
        case bento::protos::Value_Primitive::kBoolean:
            name += "Boolean";
            break;
        case bento::protos::Value_Primitive::VALUE_NOT_SET:
            name += "None";
            break;
        default:
            name += "UNHANDLED TYPE";
    }
    name += "]";
    return name;
}

std::string valStoredTypeName(const bento::protos::Value_Array& val) {
    // The array type technically allows for different types in each element
    // The array type is guessed here from the first element, if any
    if (val.values_size() != 0) {
        return "Array[Probably " + valStoredTypeName(val.values(0)) + "]";
    }
    return "Array[Unknown]";
}

// Returns a name for what the Value stores
std::string valStoredTypeName(const bento::protos::Value& val) {
    if (val.has_primitive()) {
        return valStoredTypeName(val.primitive());
    } else if (val.has_array()) {
        return valStoredTypeName(val.array());
    }

    return "None";
}

// Returns a name for what the Value says it stores under its data_type
std::string valDataTypeName(const bento::protos::Type_Primitive& valType) {
    std::string name = "Primitive.DataType[";
    switch (valType) {
        case bento::protos::Type_Primitive_INVALID:
            name += "Invalid";
            break;
        case bento::protos::Type_Primitive_BYTE:
            name += "Byte";
            break;
        case bento::protos::Type_Primitive_INT32:
            name += "32-bit Integer";
            break;
        case bento::protos::Type_Primitive_INT64:
            name += "64-bit Integer";
            break;
        case bento::protos::Type_Primitive_FLOAT32:
            name += "32-bit Float";
            break;
        case bento::protos::Type_Primitive_FLOAT64:
            name += "64-bit Float";
            break;
        case bento::protos::Type_Primitive_BOOL:
            name += "Boolean";
            break;
        case bento::protos::Type_Primitive_STRING:
            name += "String";
            break;
        default:
            name += "Unknown";
    }

    name += "]";
    return name;
}

std::string valDataTypeName(const bento::protos::Type_Array& valType) {
    std::string name = "Array[(";

    // Add the dimensions
    if (valType.dimensions_size() != 0) {
        name += std::to_string(valType.dimensions(0));
    }
    for (size_t i = 1; i < valType.dimensions_size(); ++i) {
        name += ", " + std::to_string(valType.dimensions(i));
    }
    name += "), dtype=";
    name += valDataTypeName(valType.element_type());
    name += "]";
    return name;
}

std::string valDataTypeName(const bento::protos::Type& valType) {
    switch (valType.kind_case()) {
        case bento::protos::Type::kPrimitive:
            return valDataTypeName(valType.primitive());
        case bento::protos::Type::kArray:
            return valDataTypeName(valType.array());
        case bento::protos::Type::KIND_NOT_SET:
            return "None";
        default:
            return "UNHANDLED TYPE";
    }
}

}

#include <proto/valueType.h>

namespace proto {

std::string valStoredTypeName(const bento::protos::Value_Primitive& val) {
    std::string name = "Primitive[";
    auto typeEnumVal = val.value_case();
    name += bento::protos::Value_Primitive::descriptor()
                ->FindFieldByNumber(typeEnumVal)
                ->name();
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
    name += bento::protos::Type_Primitive_Name(valType);
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

}  // namespace proto

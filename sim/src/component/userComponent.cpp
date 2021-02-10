#include <component/userComponent.h>
#include <google/protobuf/util/message_differencer.h>

namespace ics::component {

const bento::protos::Value& UserComponent::getValue(
    const std::string& attrName) {
    return getMutableValue(attrName);
}

bento::protos::Value& UserComponent::getMutableValue(
    const std::string& attrName) {
    return values[attrName];
}

void UserComponent::setValue(const std::string& attrName,
                             const bento::protos::Value& value) {
    if (!compDef.schema().contains(attrName)) {
        throw std::out_of_range("No such attribute name: " + attrName);
    }

    if (!value.has_data_type()) {
        throw std::runtime_error(
            "Missing data type when setting value for attribute " + attrName);
    }

    auto schemaType = compDef.schema().at(attrName);
    auto differencer = google::protobuf::util::MessageDifferencer();
    if (!differencer.Compare(schemaType, value.data_type())) {
        throw std::runtime_error(
            "Data type of given value does not match schema type for "
            "attribute " +
            attrName);
    }

    values[attrName] = value;
}

}  // namespace ics::component

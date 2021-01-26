#include <component/userComponent.h>

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

    values[attrName] = value;
}

}  // namespace ics::component

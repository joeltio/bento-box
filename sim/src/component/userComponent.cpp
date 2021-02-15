#include <component/userComponent.h>
#include <google/protobuf/util/message_differencer.h>
#include <proto/valueType.h>
#include <proto/userValue.h>

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

    // Ensure that data_type and value match
    if (!proto::valHasCorrectDataType(value)) {
        throw std::runtime_error(
            "Data stored in value and data type stored in value do not match. "
            "Data stored type: " +
            proto::valStoredTypeName(value) +
            ", data type: " + proto::valDataTypeName(value.data_type()));
    }

    auto& valToSet = values[attrName];
    auto& schemaType = compDef.schema().at(attrName);
    if (schemaType.has_array()) {
        // Just set the array value completely
        valToSet = value;
        return;
    }

    // TODO(joeltio): Streamline this together with eqOp
    // If schemaType and value are numeric, try to convert
    if (proto::isTypeOfTypes<proto_NUMERIC>(schemaType) &&
        proto::isValOfTypes<proto_NUMERIC>(value)) {
        proto::runFnWithVal<proto_NUMERIC>(
            value, [&valToSet, &schemaType]<class X>(X x) {
                proto::runFnWithValType<proto_NUMERIC>(
                    schemaType, [&valToSet, &x]<class Y>(Y* _) {
                        proto::setVal(valToSet, (Y)x);
                    });

                // Return something random since it is required
                return 3;
            });
        return;
    }

    // Otherwise, require that the value's data_type is the same as the
    // schemaType
    auto differencer = google::protobuf::util::MessageDifferencer();
    // Ensure that the data_types between schema and value match
    if (!differencer.Compare(value.data_type(), schemaType)) {
        throw std::runtime_error(
            "Data type of given value does not match component's schemaType "
            "for "
            "attribute " +
            attrName + ". Expected: " + proto::valDataTypeName(schemaType) +
            ", Got: " + proto::valDataTypeName(value.data_type()) + ".");
    }

    valToSet = value;
}

}  // namespace ics::component

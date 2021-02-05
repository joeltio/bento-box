#include <interpreter/util.h>
#include <index/entityIndex.h>

namespace interpreter {

bento::protos::AttributeRef createAttrRef(
    const char* compName, ics::index::EntityIndex::EntityId entityId,
    const char* attrName) {
    auto attrRef = bento::protos::AttributeRef();
    attrRef.set_component(compName);
    attrRef.set_entity_id(entityId);
    attrRef.set_attribute(attrName);
    return attrRef;
}

bento::protos::ComponentDef createSimpleCompDef(
    const char* name,
    std::initializer_list<std::pair<const char*, bento::protos::Type_Primitive>>
        schema) {
    auto compDef = bento::protos::ComponentDef();
    compDef.set_name(name);
    for (auto compSchema = compDef.mutable_schema();
         const auto& pair : schema) {
        auto type = bento::protos::Type();
        type.set_primitive(pair.second);
        compSchema->operator[](pair.first) = type;
    }

    return compDef;
}

}  // namespace interpreter

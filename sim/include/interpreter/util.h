#ifndef BENTOBOX_UTIL_H
#define BENTOBOX_UTIL_H

#include <bento/protos/ecs.pb.h>
#include <bento/protos/references.pb.h>
#include <index/entityIndex.h>

namespace interpreter {

bento::protos::AttributeRef createAttrRef(
    const char* compName, ics::index::EntityIndex::EntityId entityId,
    const char* attrName);

// Creates a component definition which only includes primitives
bento::protos::ComponentDef createSimpleCompDef(
    const char* name,
    std::initializer_list<std::pair<const char*, bento::protos::Type_Primitive>>
        schema);

}  // namespace interpreter

#endif  // BENTOBOX_UTIL_H

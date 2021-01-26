#ifndef BENTOBOX_USERCOMPONENT_H
#define BENTOBOX_USERCOMPONENT_H

#include <cstddef>
#include <string>
#include <variant>
#include <climits>
#include <unordered_map>
#include "bento/protos/types.pb.h"
#include "bento/protos/values.pb.h"
#include "bento/protos/ecs.pb.h"

namespace ics::component {

class UserComponent : public ics::BaseComponent {
   private:
    // Stores a map from attribute name to value.
    std::unordered_map<std::string, bento::protos::Value> values;

   public:
    // Since we can't programmatically make new types, the component types are
    // differentiated by this type name.
    const std::string typeName;

    // Stores the component definition
    const bento::protos::ComponentDef compDef;

    UserComponent(std::string typeName, bento::protos::ComponentDef compDef)
        : typeName(typeName), compDef(compDef) {}
};
}  // namespace ics::component

#endif  // BENTOBOX_USERCOMPONENT_H

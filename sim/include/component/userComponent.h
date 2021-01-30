#ifndef BENTOBOX_USERCOMPONENT_H
#define BENTOBOX_USERCOMPONENT_H

#include <string>
#include <unordered_map>
#include <core/ics/component.h>
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
    std::string typeName;

    // Stores the component definition
    bento::protos::ComponentDef compDef;

    UserComponent(std::string typeName, bento::protos::ComponentDef compDef)
        : typeName(std::move(typeName)), compDef(std::move(compDef)) {}

    const bento::protos::Value& getValue(const std::string& attrName);
    bento::protos::Value& getMutableValue(const std::string& attrName);

    void setValue(const std::string& attrName,
                  const bento::protos::Value& value);
};
}  // namespace ics::component

#endif  // BENTOBOX_USERCOMPONENT_H

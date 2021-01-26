#ifndef BENTOBOX_COMPONENTTYPEINDEX_H
#define BENTOBOX_COMPONENTTYPEINDEX_H

#include <core/ics/component.h>
#include <core/ics/componentSet.h>

#include <string>
#include <functional>
#include <unordered_map>

namespace ics::index {
class ComponentTypeIndex {
   private:
    std::unordered_map<std::string, CompGroup> typeNameGroupMap;
    CompGroup compGroup = 0;

   public:
    // The definition needs to be in the header file as the return type is auto
    // The return type is left as auto so that the capturing lambda is properly
    // represented. Type errors can occur at build-time when using function
    // pointer return types or std::function.
    auto filterCompType(const std::string& name) {
        auto compIndex = typeNameGroupMap.at(name);

        return [compIndex](const ics::ComponentSet& compSet) {
            // TODO(joeltio): find a way to make this more memory efficient
            ics::ComponentSet newSet;
            for (const CompStoreId& comp : compSet) {
                if (comp.first == compIndex) {
                    newSet.insert(comp);
                }
            }

            return newSet;
        };
    }

    bool hasComponentType(const std::string& name);

    CompGroup addComponentType(const std::string& name);

    CompGroup getComponentType(const std::string& name);
};
}  // namespace ics::index

#endif  // BENTOBOX_COMPONENTTYPEINDEX_H

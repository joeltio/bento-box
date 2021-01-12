#ifndef BENTOBOX_COMPONENTTYPEINDEX_H
#define BENTOBOX_COMPONENTTYPEINDEX_H

#include <unordered_map>
#include <functional>
#include <core/ics/component.h>
#include <core/ics/componentSet.h>

namespace ics::index {
    class ComponentTypeIndex {
    private:
        std::unordered_map<std::type_index, CompGroup> typeGroupMap;
        CompGroup compGroup = 0;

    public:
        template<Component C>
        // The return type is left as auto so that the capturing lambda is properly
        // represented. Type errors can occur at build-time when using function
        // pointer return types or std::function.
        auto filterCompType() {
            auto compIndex = typeGroupMap.at(std::type_index(typeid(C)));

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

        template<Component C>
        bool hasComponentType() {
            auto compType = std::type_index(typeid(C));
            return typeGroupMap.contains(compType);
        }

        template<Component C>
        CompGroup addComponentType() {
            auto compType = std::type_index(typeid(C));
            if (!typeGroupMap.contains(compType)) {
                typeGroupMap.insert(std::make_pair(compType, compGroup));

                // Equivalent to return compGroup++;
                auto insertedCompGroup = compGroup;
                ++compGroup;
                return insertedCompGroup;
            }

            return typeGroupMap.at(compType);
        }

        template<Component C>
        CompGroup getComponentType() {
            auto compType = std::type_index(typeid(C));
            return typeGroupMap.at(compType);
        }
    };
}


#endif //BENTOBOX_COMPONENTTYPEINDEX_H

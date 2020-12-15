#ifndef BENTOBOX_COMPONENTTYPEINDEX_H
#define BENTOBOX_COMPONENTTYPEINDEX_H

#include <unordered_map>
#include <functional>
#include <core/ics/component.h>
#include <core/ics/componentSet.h>

namespace ics::index {
    class ComponentType {
    private:
        std::unordered_map<std::type_index, size_t> map;
        size_t compTypeIndex = 0;

    public:
        template<Component C>
        // The return type is left as auto so that the capturing lambda is properly
        // represented. Type errors can occur at build-time when using function
        // pointer return types or std::function.
        auto is() {
            auto compIndex = map.at(std::type_index(typeid(C)));

            return [compIndex](const ics::ComponentSet& compSet) {
                // TODO: find a way to make this more memory efficient
                ics::ComponentSet newSet;
                for (const std::pair<size_t, CompId>& comp : compSet) {
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
            return map.contains(compType);
        }

        template<Component C>
        size_t addComponentType() {
            auto compType = std::type_index(typeid(C));
            if (!map.contains(compType)) {
                map.insert(std::make_pair(compType, compTypeIndex));
                return compTypeIndex++;
            } else {
                return map.at(compType);
            }
        }

        template<Component C>
        size_t getComponentType() {
            auto compType = std::type_index(typeid(C));
            return map.at(compType);
        }
    };
}


#endif //BENTOBOX_COMPONENTTYPEINDEX_H

#include <index/componentTypeIndex.h>

namespace ics::index {

bool ComponentTypeIndex::hasComponentType(const std::string& name) {
    return typeNameGroupMap.contains(name);
}

CompGroup ComponentTypeIndex::addComponentType(const std::string& name) {
    if (!typeNameGroupMap.contains(name)) {
        typeNameGroupMap.insert(std::make_pair(name, compGroup));

        // Equivalent to return compGroup++;
        auto insertedCompGroup = compGroup;
        ++compGroup;
        return insertedCompGroup;
    }

    return typeNameGroupMap.at(name);
}

CompGroup ComponentTypeIndex::getComponentType(const std::string& name) {
    return typeNameGroupMap.at(name);
}

}  // namespace ics::index
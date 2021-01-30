#include <ics.h>

namespace ics {
component::UserComponent& getComponent(index::IndexStore& indexStore,
                                       ComponentStore& compStore,
                                       const std::string& typeName,
                                       index::EntityIndex::EntityId entityId) {
    auto& compTypeIndex = indexStore.componentType;
    auto& entityIndex = indexStore.entity;

    auto components = util::Composable<ComponentStore&>(compStore) |
                      ics::asCompSet | compTypeIndex.filterCompType(typeName) |
                      entityIndex.filterEntityId(entityId);

    if (components.data.size() > 1) {
        throw std::logic_error(
            "More than one component match entity and type.");
    } else if (components.data.empty()) {
        throw std::runtime_error(
            "No component with typeName and entityId found.");
    }

    auto compStoreId = *components.data.begin();
    return getComponent<component::UserComponent>(compStore, compStoreId);
}
}  // namespace ics
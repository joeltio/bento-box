#include <index/entityIndex.h>

namespace ics::index {

EntityIndex::EntityId EntityIndex::addEntityId() {
    // Update the next entity id
    auto entityId = nextEntityId;
    nextEntityId++;

    // Update the entityCompMap
    entityCompMap.emplace(entityId, std::unordered_set<CompStoreId>());
    return entityId;
}

void EntityIndex::addComponent(EntityId entityId,
                               const CompStoreId& compStoreId) {
    entityCompMap.at(entityId).insert(compStoreId);
}

std::unordered_set<CompStoreId> EntityIndex::getComponents(
    EntityId entityId) const {
    return entityCompMap.at(entityId);
}

void EntityIndex::removeComponent(EntityId entityId,
                                  const CompStoreId& compStoreId) {
    entityCompMap.at(entityId).erase(compStoreId);
}

}  // namespace ics::index
#ifndef BENTOBOX_ENTITYINDEX_H
#define BENTOBOX_ENTITYINDEX_H

#include <unordered_set>
#include <core/ics/componentStore.h>
#include <core/ics/util/setIntersection.h>

namespace ics::index {

    class EntityIndex {
    public:
        typedef unsigned int EntityId;
    private:
        EntityId nextEntityId = 0;
        std::unordered_map<EntityId, std::unordered_set<CompStoreId>> entityCompMap;
    public:
        // Creates a filter to find CompStoreIds with the given entityId.
        // Returns a lambda which is the filter. The lambda has the following signature:
        // ComponentSet -> ComponentSet
        auto filterEntityId(EntityId entityId) {
            return [this, entityId](const ics::ComponentSet& compSet) -> ics::ComponentSet {
                const auto& compStoreIds = this->entityCompMap.at(entityId);
                return util::setIntersection(compStoreIds, compSet);
            };
        }

        EntityId addEntityId() {
            // Update the next entity id
            auto entityId = nextEntityId;
            nextEntityId++;

            // Update the entityCompMap
            entityCompMap.emplace(entityId, std::unordered_set<CompStoreId>());
            return entityId;
        }

        void addComponent(EntityId entityId, const CompStoreId& compStoreId) {
            entityCompMap.at(entityId).insert(compStoreId);
        }

        std::unordered_set<CompStoreId> getComponents(EntityId entityId) const {
            return entityCompMap.at(entityId);
        }

        void removeComponent(EntityId entityId, const CompStoreId& compStoreId) {
            entityCompMap.at(entityId).erase(compStoreId);
        }
    };
}

#endif //BENTOBOX_ENTITYINDEX_H

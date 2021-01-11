#ifndef BENTOBOX_ENTITY_H
#define BENTOBOX_ENTITY_H

#include <unordered_set>
#include <core/ics/componentStore.h>
#include <core/ics/util/setIntersection.h>

namespace ics::index {

    class Entity {
    public:
        typedef unsigned int EntityId;
    private:
        EntityId nextEntityId = 0;
        std::unordered_map<EntityId, std::unordered_set<CompStoreId>> entityCompMap;
    public:
        auto id(EntityId entityId) {
            return [this, entityId](const ics::ComponentSet& compSet) {
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

#endif //BENTOBOX_ENTITY_H

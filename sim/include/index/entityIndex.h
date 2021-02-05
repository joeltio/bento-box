#ifndef BENTOBOX_ENTITYINDEX_H
#define BENTOBOX_ENTITYINDEX_H

#include <ranges>
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
    // Returns a lambda which is the filter. The lambda has the following
    // signature: ComponentSet -> ComponentSet
    // The definition needs to be in the header file for return type deduction
    auto filterEntityId(EntityId entityId) {
        return [this, entityId](
                   const ics::ComponentSet& compSet) -> ics::ComponentSet {
            const auto& compStoreIds = this->entityCompMap.at(entityId);
            return util::setIntersection(compStoreIds, compSet);
        };
    }

    EntityId addEntityId();

    // Start with certain entity IDs
    template <class T>
    // Require that the input is an iterable, and the value stored in the
    // iterable is an EntityId
    requires std::ranges::range<T>&&
        std::is_same_v<std::ranges::range_value_t<T>, EntityId> void
        setEntityIds(T ids) {
        EntityId maxId = 0;
        for (auto id : ids) {
            if (id > maxId) {
                maxId = id;
            }

            entityCompMap.emplace(id, std::unordered_set<CompStoreId>());
        }
        nextEntityId = maxId + 1;
    }

    void addComponent(EntityId entityId, const CompStoreId& compStoreId);

    std::unordered_set<CompStoreId> getComponents(EntityId entityId) const;

    void removeComponent(EntityId entityId, const CompStoreId& compStoreId);
};
}  // namespace ics::index

#endif  // BENTOBOX_ENTITYINDEX_H

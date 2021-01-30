#ifndef BENTOBOX_COMPONENTSTOREEXT_H
#define BENTOBOX_COMPONENTSTOREEXT_H

#include <component/userComponent.h>
#include <core/ics/component.h>
#include <core/ics/componentStore.h>
#include <index/componentTypeIndex.h>
#include <index/indexStore.h>
#include <core/ics/util/composable.h>

namespace ics {
template <class C>
requires std::is_base_of_v<component::UserComponent, C> CompStoreId
addComponent(index::IndexStore& indexStore, ComponentStore& compStore,
             const C& c) {
    auto& compTypeIndex = indexStore.componentType;

    // Update the ComponentType index
    auto compIndex = compTypeIndex.addComponentType(c.typeName);
    // Add the component to the component store
    auto compId = addComponent(compStore, c, compIndex);

    return compId;
}

component::UserComponent& getComponent(index::IndexStore& indexStore,
                                       ComponentStore& compStore,
                                       const std::string& typeName,
                                       index::EntityIndex::EntityId entityId);
}  // namespace ics

#endif  // BENTOBOX_COMPONENTSTOREEXT_H

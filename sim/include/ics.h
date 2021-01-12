#ifndef BENTOBOX_COMPONENTSTOREEXT_H
#define BENTOBOX_COMPONENTSTOREEXT_H

#include <core/ics/component.h>
#include <core/ics/componentStore.h>
#include <index/componentTypeIndex.h>
#include <index/indexStore.h>

namespace ics {
template <Component C>
CompStoreId addComponent(index::IndexStore& indexStore,
                         ComponentStore& compStore, const C& c) {
    auto& compTypeIndex = indexStore.componentType;

    // Update the ComponentType index
    auto compIndex = compTypeIndex.addComponentType<C>();
    // Add the component to the component store
    auto compId = addComponent(compStore, c, compIndex);

    return compId;
}
}  // namespace ics

#endif  // BENTOBOX_COMPONENTSTOREEXT_H

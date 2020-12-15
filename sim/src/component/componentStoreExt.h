#ifndef BENTOBOX_COMPONENTSTOREEXT_H
#define BENTOBOX_COMPONENTSTOREEXT_H

#include <core/ics/component.h>
#include <core/ics/componentStore.h>
#include <core/ics/indexStore.h>
#include "../index/componentType.h"

namespace ics {
    template<Component C>
    std::pair<size_t, CompId> addComponent(IndexStore& indexStore, ComponentStore& compStore, const C& c) {
        auto& compTypeIndex = indexStore.at<ics::index::ComponentType>();

        // Update the ComponentType index
        auto compIndex = compTypeIndex.addComponentType<C>();
        // Add the component to the component store
        auto compId = addComponent(compStore, c, compIndex);

        return compId;
    }
}

#endif //BENTOBOX_COMPONENTSTOREEXT_H

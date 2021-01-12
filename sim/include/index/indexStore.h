#ifndef BENTOBOX_INDEXSTORE_H
#define BENTOBOX_INDEXSTORE_H

#include "componentTypeIndex.h"
#include "entityIndex.h"

namespace ics::index {
struct IndexStore {
    ComponentTypeIndex componentType;
    EntityIndex entity;
};
}  // namespace ics::index

#endif  // BENTOBOX_INDEXSTORE_H

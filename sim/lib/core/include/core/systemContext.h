#ifndef BENTOBOX_SYSTEMCONTEXT_H
#define BENTOBOX_SYSTEMCONTEXT_H

#include <forward_list>
#include <functional>
#include "ics/componentStore.h"
#include "graphicsContext.h"

template<class IndexStore>
using SystemFn = std::function<void(GraphicsContext&, ics::ComponentStore&, IndexStore&)>;

template<class IndexStore>
struct SystemContext {
    std::forward_list<SystemFn<IndexStore>> systems;
    void run(GraphicsContext& graphicsContext, ics::ComponentStore& componentStore, IndexStore& indexStore) {
        for (const auto& system : systems) {
            system(graphicsContext, componentStore, indexStore);
        }
    }
};

#endif //BENTOBOX_SYSTEMCONTEXT_H

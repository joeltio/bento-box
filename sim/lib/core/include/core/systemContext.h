#ifndef BENTOBOX_SYSTEMCONTEXT_H
#define BENTOBOX_SYSTEMCONTEXT_H

#include <forward_list>
#include <functional>

#include "graphicsContext.h"
#include "ics/componentStore.h"

namespace {
template <class C>
concept IndexStore = std::semiregular<C> && !std::is_fundamental_v<C>;
}

template <IndexStore IS>
using SystemFn =
    std::function<void(GraphicsContext&, ics::ComponentStore&, IS&)>;

template <IndexStore IS>
struct SystemContext {
    std::forward_list<SystemFn<IS>> systems;
    void run(GraphicsContext& graphicsContext,
             ics::ComponentStore& componentStore, IS& indexStore) {
        for (const auto& system : systems) {
            system(graphicsContext, componentStore, indexStore);
        }
    }
};

#endif  // BENTOBOX_SYSTEMCONTEXT_H

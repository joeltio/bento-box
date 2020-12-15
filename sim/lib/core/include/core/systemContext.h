#ifndef BENTOBOX_SYSTEMCONTEXT_H
#define BENTOBOX_SYSTEMCONTEXT_H

#include <forward_list>
#include <functional>
#include "ics/componentStore.h"
#include "ics/indexStore.h"
#include "graphicsContext.h"

typedef std::function<void(GraphicsContext&, ics::ComponentStore&, ics::IndexStore&)> SystemFn;

struct SystemContext {
    std::forward_list<SystemFn> systems;
    void run(GraphicsContext& graphicsContext, ics::ComponentStore& componentStore, ics::IndexStore& indexStore);
};

#endif //BENTOBOX_SYSTEMCONTEXT_H

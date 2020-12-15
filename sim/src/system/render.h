#ifndef BENTOBOX_RENDER_H
#define BENTOBOX_RENDER_H

#include <core/graphicsContext.h>
#include <core/ics/componentStore.h>
#include <core/ics/indexStore.h>

namespace ics::system {
    void render(GraphicsContext& graphicsContext, ics::ComponentStore& componentStore, ics::IndexStore& indexStore);
}

#endif //BENTOBOX_RENDER_H

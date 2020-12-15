#include <core/systemContext.h>

void SystemContext::run(
    GraphicsContext& graphicsContext,
    ics::ComponentStore& componentStore,
    ics::IndexStore& indexStore
) {
    for (const auto& system : systems) {
        system(graphicsContext, componentStore, indexStore);
    }
}

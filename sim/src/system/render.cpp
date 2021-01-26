#include <component/textureComponent.h>
#include <core/ics/componentStore.h>
#include <core/ics/util/composable.h>
#include <system/render.h>

#include <iostream>

namespace ics::system {
void render(GraphicsContext &graphicsContext,
            ics::ComponentStore &componentStore,
            ics::index::IndexStore &indexStore) {
    auto &componentType = indexStore.componentType;
    auto components =
        util::Composable<ComponentStore &>(componentStore) | ics::asCompSet |
        componentType.filterCompType(ics::component::TEXTURE2D_COMPONENT_NAME);

    for (auto componentId : components.data) {
        auto component = ics::getComponent<ics::component::Texture2DComponent>(
            componentStore, componentId);
        // TODO(joeltio): Use the graphics context to render the texture
        std::cout << "texture: " << component.getValue("texture").primitive().float_64() << std::endl;
    }
}
}  // namespace ics::system

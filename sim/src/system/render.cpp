#include <system/render.h>
#include <iostream>

#include <component/textureComponent.h>
#include <core/ics/componentStore.h>
#include <core/ics/util/composable.h>

namespace ics::system {
    void render(GraphicsContext &graphicsContext, ics::ComponentStore &componentStore, ics::index::IndexStore &indexStore) {
        auto& componentType = indexStore.componentType;
        auto components = util::Composable<ComponentStore&>(componentStore)
            | ics::asCompSet
            | componentType.filterCompType<ics::component::Texture2DComponent>();

        for (auto componentId : components.data) {
            auto component = ics::getComponent<ics::component::Texture2DComponent>(componentStore, componentId);
            // TODO(joeltio): Use the graphics context to render the texture
            std::cout << "texture: " << component.texture << std::endl;
        }
    }
}

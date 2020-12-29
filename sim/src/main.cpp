#include <core/systemContext.h>
#include <core/windowContext.h>
#include <core/graphicsContext.h>
#include <index/componentType.h>
#include <component/textureComponent.h>
#include <system/render.h>
#include <ics.h>

int main() {
    WindowContext windowContext = WindowContext(800, 600, "Bento Box");
    GraphicsContext graphics = GraphicsContext(windowContext);
    ics::ComponentStore componentStore = ics::ComponentStore();
    ics::IndexStore indexStore = ics::IndexStore();
    SystemContext systemContext = SystemContext();

    // Setup indexStore
    auto compTypeIndex = ics::index::ComponentType();
    compTypeIndex.addComponentType<ics::component::Texture2DComponent>();
    indexStore.insert(compTypeIndex);

    auto tex1 = ics::component::Texture2DComponent(1);
    auto tex2 = ics::component::Texture2DComponent(2);
    auto tex3 = ics::component::Texture2DComponent(3);
    auto tex4 = ics::component::Texture2DComponent(4);
    ics::addComponent(indexStore, componentStore, tex1);
    ics::addComponent(indexStore, componentStore, tex2);
    ics::addComponent(indexStore, componentStore, tex3);
    ics::addComponent(indexStore, componentStore, tex4);

    const SystemFn a(&ics::system::render);
    systemContext.systems.push_front(a);

    while(!windowContext.shouldClose())
    {
        glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);

        systemContext.run(graphics, componentStore, indexStore);

        windowContext.swapBuffers();
        windowContext.updateEvents();
    }
}

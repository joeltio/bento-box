#include <component/textureComponent.h>
#include <core/graphicsContext.h>
#include <core/systemContext.h>
#include <core/windowContext.h>
#include <ics.h>
#include <system/render.h>

int main() {
    WindowContext windowContext = WindowContext(800, 600, "Bento Box");
    GraphicsContext graphics = GraphicsContext(windowContext);
    ics::ComponentStore componentStore = ics::ComponentStore();
    ics::index::IndexStore indexStore = ics::index::IndexStore();
    SystemContext systemContext = SystemContext<ics::index::IndexStore>();

    auto tex1 = ics::component::Texture2DComponent(1);
    auto tex2 = ics::component::Texture2DComponent(2);
    auto tex3 = ics::component::Texture2DComponent(3);
    auto tex4 = ics::component::Texture2DComponent(4);
    ics::addComponent(indexStore, componentStore, tex1);
    ics::addComponent(indexStore, componentStore, tex2);
    ics::addComponent(indexStore, componentStore, tex3);
    ics::addComponent(indexStore, componentStore, tex4);

    const SystemFn<ics::index::IndexStore> a(&ics::system::render);
    systemContext.systems.push_front(a);

    while (!windowContext.shouldClose()) {
        glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);

        systemContext.run(graphics, componentStore, indexStore);

        windowContext.swapBuffers();
        windowContext.updateEvents();
    }
}

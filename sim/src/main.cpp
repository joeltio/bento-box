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

    auto tex1 = ics::component::Texture2DComponent();
    auto value = bento::protos::Value();
    value.mutable_primitive()->set_int_64(1);
    tex1.setValue("texture", value);

    auto tex2 = ics::component::Texture2DComponent();
    value = bento::protos::Value();
    value.mutable_primitive()->set_int_64(2);
    tex2.setValue("texture", value);

    auto tex3 = ics::component::Texture2DComponent();
    value = bento::protos::Value();
    value.mutable_primitive()->set_int_64(3);
    tex3.setValue("texture", value);

    auto tex4 = ics::component::Texture2DComponent();
    value = bento::protos::Value();
    value.mutable_primitive()->set_int_64(4);
    tex4.setValue("texture", value);

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

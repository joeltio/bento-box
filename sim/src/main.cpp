#include "WindowContext.h"
#include "GraphicsContext.h"
#include <iostream>

int main() {
    WindowContext windowContext = WindowContext(800, 600, "Bento Box");
    GraphicsContext graphics = GraphicsContext(windowContext);

    while(!windowContext.shouldClose())
    {
        glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);

        windowContext.swapBuffers();
        windowContext.updateEvents();
    }
}

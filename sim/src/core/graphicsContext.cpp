#include "graphicsContext.h"

GraphicsContext::GraphicsContext(WindowContext& windowContext) : windowContext(windowContext) {
    if (!gladLoadGLLoader((GLADloadproc) glfwGetProcAddress)) {
        throw "Failed to initialise GLAD";
    }
}

GraphicsContext::~GraphicsContext() {}

GraphicsContext::GraphicsContext(const GraphicsContext &other) : windowContext(other.windowContext) {}

GraphicsContext& GraphicsContext::operator=(const GraphicsContext &other) {
    windowContext = other.windowContext;
    return *this;
}

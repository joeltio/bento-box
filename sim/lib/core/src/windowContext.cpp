#include <core/windowContext.h>

namespace {
    void framebufferSizeCallback([[maybe_unused]] GLFWwindow* window, int width, int height) {
        glViewport(0, 0, width, height);
    }
}

WindowContext::WindowContext(
    int width, int height, const char *title
) : width(width), height(height), title(title) {
    // Initialise GLFW
    glfwInit();
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    // Required for Mac
    // glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);

    // Create window
    window = glfwCreateWindow(width, height, title, nullptr, nullptr);
    if (window == nullptr) {
        // TODO(joeltio): Create an exception for this
        throw "Failed to create GLFW window";
    }

    glfwMakeContextCurrent(window);
    glfwSetFramebufferSizeCallback(window, framebufferSizeCallback);
}

WindowContext::~WindowContext() {
    glfwTerminate();
}

WindowContext::WindowContext(
    const WindowContext &other
) : width(other.width), height(other.height), title(other.title) {
    // Create a new window with the same parameters
    window = glfwCreateWindow(
        other.width,
        other.height,
        other.title,
        nullptr,
        nullptr
    );
    if (window == nullptr) {
        // TODO(joeltio): Create an exception for this
        throw "Failed to create GLFW window";
    }
}

WindowContext& WindowContext::operator=(const WindowContext &other) = default;

bool WindowContext::isCurrentContext() const {
    return glfwGetCurrentContext() == window;
}

void WindowContext::makeCurrentContext() const {
    glfwMakeContextCurrent(window);
}

bool WindowContext::shouldClose() const {
    return glfwWindowShouldClose(window);
}

void WindowContext::updateEvents() { // NOLINT(readability-convert-member-functions-to-static)
    // This function is not made static to cater to other implementations which
    // may require the window variable
    glfwPollEvents();
}

void WindowContext::swapBuffers() const {
    glfwSwapBuffers(window);
}

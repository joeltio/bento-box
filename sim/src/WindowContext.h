#ifndef BENTOBOX_WINDOWCONTEXT_H
#define BENTOBOX_WINDOWCONTEXT_H

#include <glad/glad.h>
#include <GLFW/glfw3.h>

class WindowContext {
private:
    int width;
    int height;
    const char* title;
public:
    GLFWwindow* window = nullptr;

    WindowContext(int width, int height, const char* title);
    ~WindowContext();
    WindowContext(const WindowContext& other);
    WindowContext& operator=(const WindowContext& other);

    bool isCurrentContext() const;
    void makeCurrentContext() const;
    bool shouldClose() const;
    void updateEvents();
    void swapBuffers() const;
};

#endif //BENTOBOX_WINDOWCONTEXT_H

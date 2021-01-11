#define STB_IMAGE_IMPLEMENTATION

#include <core/graphicsContext.h>
#include <stb_image.h>

#include <stdexcept>

GraphicsContext::GraphicsContext(WindowContext& windowContext)
    : windowContext(windowContext) {
    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
        throw "Failed to initialise GLAD";
    }
}

GraphicsContext::~GraphicsContext() {
    glBindTexture(GL_TEXTURE_2D, 0);

    for (const auto& pathTexIdPair : textureCache) {
        glDeleteTextures(1, &pathTexIdPair.second);
    }
}

// The default copy assignment is unable to assign references, hence they must
// be explicitly defined. The linting is disabled for this reason.
GraphicsContext& GraphicsContext::operator=(
    const GraphicsContext& other) {  // NOLINT(modernize-use-equals-default)
    windowContext = other.windowContext;
    textureCache = other.textureCache;
    return *this;
}

unsigned int GraphicsContext::loadTexture2D(const std::string& filepath) {
    if (textureCache.find(filepath) != textureCache.end()) {
        return textureCache[filepath];
    }

    unsigned int texture;
    glGenTextures(1, &texture);
    glBindTexture(GL_TEXTURE_2D, texture);

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

    int width, height, nrChannels;
    unsigned char* data =
        stbi_load(filepath.c_str(), &width, &height, &nrChannels, 0);

    if (!data) {
        // TODO(joeltio): Replace with a logger class and add name of texture
        // that failed to load
        throw std::runtime_error("Failed to load texture.");
    }

    if (nrChannels == 4) {
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA,
                     GL_UNSIGNED_BYTE, data);
    } else if (nrChannels == 3) {
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB,
                     GL_UNSIGNED_BYTE, data);
    } else {
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RED,
                     GL_UNSIGNED_BYTE, data);
    }

    glGenerateMipmap(GL_TEXTURE_2D);
    textureCache[filepath] = texture;

    stbi_image_free(data);
    return texture;
}

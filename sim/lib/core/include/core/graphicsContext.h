#ifndef BENTOBOX_GRAPHICSCONTEXT_H
#define BENTOBOX_GRAPHICSCONTEXT_H

#include <string>
#include <unordered_map>
#include "windowContext.h"

class GraphicsContext {
private:
    std::unordered_map<std::string, unsigned int> textureCache;
public:
    GraphicsContext(WindowContext& windowContext);
    ~GraphicsContext();
    GraphicsContext(const GraphicsContext& other) = default;
    GraphicsContext& operator=(const GraphicsContext& other);

    WindowContext& windowContext;

    unsigned int loadTexture2D(std::string const& filepath);
};

#endif //BENTOBOX_GRAPHICSCONTEXT_H

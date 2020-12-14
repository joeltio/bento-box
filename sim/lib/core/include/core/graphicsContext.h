#ifndef BENTOBOX_GRAPHICSCONTEXT_H
#define BENTOBOX_GRAPHICSCONTEXT_H

#include <string>
#include <unordered_map>
#include "windowContext.h"

class GraphicsContext {
public:
    GraphicsContext(WindowContext& windowContext);
    ~GraphicsContext();
    GraphicsContext(const GraphicsContext& other);
    GraphicsContext& operator=(const GraphicsContext& other);

    WindowContext& windowContext;

    std::unordered_map<std::string, unsigned int> textureCache;
    unsigned int loadTexture2D(std::string const& filepath);
};

#endif //BENTOBOX_GRAPHICSCONTEXT_H

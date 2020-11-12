#ifndef BENTOBOX_GRAPHICSCONTEXT_H
#define BENTOBOX_GRAPHICSCONTEXT_H

#include "WindowContext.h"

class GraphicsContext {
public:
    GraphicsContext(WindowContext& windowContext);
    ~GraphicsContext();
    GraphicsContext(const GraphicsContext& other);
    GraphicsContext& operator=(const GraphicsContext& other);

    WindowContext& windowContext;
};

#endif //BENTOBOX_GRAPHICSCONTEXT_H

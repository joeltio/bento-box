#ifndef BENTOBOX_TEXTURECOMPONENT_H
#define BENTOBOX_TEXTURECOMPONENT_H

#include <core/ics/component.h>

namespace ics::component {
struct Texture2DComponent : public ics::BaseComponent {
    unsigned int texture;

    explicit Texture2DComponent(unsigned int texture) : texture(texture) {}
};
}  // namespace ics::component

#endif  // BENTOBOX_TEXTURECOMPONENT_H

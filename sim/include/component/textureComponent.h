#ifndef BENTOBOX_TEXTURECOMPONENT_H
#define BENTOBOX_TEXTURECOMPONENT_H

#include <string>
#include "userComponent.h"

namespace ics::component {
const char TEXTURE2D_COMPONENT_NAME[] = "Texture2DComponent";
}

namespace {

bento::protos::ComponentDef createCompDef();

}  // namespace

namespace ics::component {
struct Texture2DComponent : public UserComponent {
    Texture2DComponent()
        : UserComponent(TEXTURE2D_COMPONENT_NAME, createCompDef()) {}
};
}  // namespace ics::component

#endif  // BENTOBOX_TEXTURECOMPONENT_H

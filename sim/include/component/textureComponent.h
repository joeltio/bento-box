#ifndef BENTOBOX_TEXTURECOMPONENT_H
#define BENTOBOX_TEXTURECOMPONENT_H

#include <string>
#include "userComponent.h"

namespace ics::component {
const char TEXTURE2D_COMPONENT_NAME[] = "Texture2DComponent";
}

namespace {

// This needs to be in the header as it is called immediately in the header as
// well.
bento::protos::ComponentDef createCompDef() {
    auto compDef = bento::protos::ComponentDef();
    compDef.set_name(ics::component::TEXTURE2D_COMPONENT_NAME);

    auto& schema = *compDef.mutable_schema();
    schema["texture"] = bento::protos::Type();
    schema["texture"].set_primitive(bento::protos::Type_Primitive_INT64);

    return compDef;
};

}  // namespace

namespace ics::component {
struct Texture2DComponent : public UserComponent {
    Texture2DComponent()
        : UserComponent(TEXTURE2D_COMPONENT_NAME, createCompDef()) {}
};
}  // namespace ics::component

#endif  // BENTOBOX_TEXTURECOMPONENT_H

#ifndef BENTOBOX_POS2DCOMPONENT_H
#define BENTOBOX_POS2DCOMPONENT_H

#include <bento/protos/ecs.pb.h>
#include <component/userComponent.h>

namespace ics::component {
const char POS2D_COMPONENT_NAME[] = "Pos2DComponent";
}

namespace {

bento::protos::ComponentDef createCompDef();

}  // namespace

namespace ics::component {
struct Pos2DComponent : public UserComponent {
    Pos2DComponent()
        : UserComponent(POS2D_COMPONENT_NAME, createCompDef()) {}
};
}  // namespace ics::component

#endif  // BENTOBOX_POS2DCOMPONENT_H

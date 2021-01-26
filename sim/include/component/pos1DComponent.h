#ifndef BENTOBOX_POS1DCOMPONENT_H
#define BENTOBOX_POS1DCOMPONENT_H

#include <bento/protos/ecs.pb.h>
#include <component/userComponent.h>

namespace ics::component {
const char POS1D_COMPONENT_NAME[] = "Pos1DComponent";
}

namespace {

bento::protos::ComponentDef createCompDef();

}  // namespace

namespace ics::component {
struct Pos1DComponent : public UserComponent {
    Pos1DComponent()
        : UserComponent(POS1D_COMPONENT_NAME, createCompDef()) {}
};
}  // namespace ics::component

#endif  // BENTOBOX_POS1DCOMPONENT_H

#include <component/pos2DComponent.h>

namespace {

bento::protos::ComponentDef createCompDef() {
    auto compDef = bento::protos::ComponentDef();
    compDef.set_name(ics::component::POS2D_COMPONENT_NAME);

    auto& schema = *compDef.mutable_schema();
    schema["x"] = bento::protos::Type();
    schema["x"].set_primitive(bento::protos::Type_Primitive_INT64);

    schema["y"] = bento::protos::Type();
    schema["y"].set_primitive(bento::protos::Type_Primitive_INT64);

    return compDef;
}

}  // namespace

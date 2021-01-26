#include <component/textureComponent.h>

namespace {

bento::protos::ComponentDef createCompDef() {
    auto compDef = bento::protos::ComponentDef();
    compDef.set_name(ics::component::TEXTURE2D_COMPONENT_NAME);

    auto& schema = *compDef.mutable_schema();
    schema["texture"] = bento::protos::Type();
    schema["texture"].set_primitive(bento::protos::Type_Primitive_INT64);

    return compDef;
}

}  // namespace
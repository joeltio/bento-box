#ifndef BENTOBOX_POS2DCOMPONENT_H
#define BENTOBOX_POS2DCOMPONENT_H

namespace ics::component {
struct Pos2DComponent : public ics::BaseComponent {
    unsigned int x;
    unsigned int y;

    Pos2DComponent(unsigned int x, unsigned int y) : x(x), y(y) {}
};
}  // namespace ics::component

#endif  // BENTOBOX_POS2DCOMPONENT_H

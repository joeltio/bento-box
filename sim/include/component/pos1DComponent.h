#ifndef BENTOBOX_POS1DCOMPONENT_H
#define BENTOBOX_POS1DCOMPONENT_H

namespace ics::component {
    struct Pos1DComponent : public ics::BaseComponent {
        unsigned int x;

        explicit Pos1DComponent(unsigned int x) : x(x) {}
    };
}

#endif //BENTOBOX_POS1DCOMPONENT_H

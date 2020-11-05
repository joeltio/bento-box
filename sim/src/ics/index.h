#ifndef BENTOBOX_INDEX_H
#define BENTOBOX_INDEX_H

#include "component.h"

namespace ics {
    template<class T>
    concept Index = requires(T a, archetypes::Component c) {
        { a.template addComponent(c) } -> std::same_as<void>;
        { a.template removeComponent(c) } -> std::same_as<void>;
    };
}

#endif //BENTOBOX_INDEX_H

#ifndef BENTOBOX_INDEX_H
#define BENTOBOX_INDEX_H

#include "component.h"

namespace ics {
    template<class T, class C>
    concept Index = Component<C>
        && requires(T a, C c) {
            { a.template addComponent<C>(c) } -> std::same_as<void>;
            { a.template removeComponent<C>(c) } -> std::same_as<void>;
        };
}

#endif //BENTOBOX_INDEX_H

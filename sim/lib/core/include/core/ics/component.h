#ifndef BENTOBOX_COMPONENT_H
#define BENTOBOX_COMPONENT_H

#include <concepts>

namespace ics {
    struct BaseComponent {
        // isActive is used for memory pooling. When a component is marked as
        // inactive, it is "deleted". The memory used by inactive components
        // will be reused.
        bool isActive = true;
        bool operator==(const BaseComponent&) const = default;
    };

    template<class C>
    concept Component = std::derived_from<C, BaseComponent>;
}

#endif //BENTOBOX_COMPONENT_H

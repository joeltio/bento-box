#ifndef BENTOBOX_COMPONENT_H
#define BENTOBOX_COMPONENT_H

#include <concepts>

namespace ics {
    struct BaseComponent {
        bool isActive = true;
        bool operator==(const BaseComponent&) const = default;
    };

    template<class C>
    concept Component = std::derived_from<C, BaseComponent>;

    struct UnknownComponent : BaseComponent { };

    static_assert(Component<UnknownComponent>);
}

#endif //BENTOBOX_COMPONENT_H

#ifndef BENTOBOX_COMPONENT_H
#define BENTOBOX_COMPONENT_H

#include <concepts>

namespace ics {
    template<class T>
    concept Component = std::movable<T>
            && std::copyable<T>
            && std::equality_comparable<T>
            && std::same_as<decltype(T::isActive), bool>;

    // Needed for Index concept
    // See: https://stackoverflow.com/q/37655113/4428725
    namespace archetypes {
        struct Component {
            bool isActive = true;
            bool operator==(const Component&) const = default;
        };
    }

    static_assert(Component<archetypes::Component>);

    struct DefaultComponent {
        bool isActive = true;
        bool operator==(const DefaultComponent&) const = default;
    };

    static_assert(Component<DefaultComponent>);
}

#endif //BENTOBOX_COMPONENT_H

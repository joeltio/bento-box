#ifndef BENTOBOX_COMPONENT_H
#define BENTOBOX_COMPONENT_H

#include <concepts>

namespace ics {
    template<class T>
    concept Component = std::movable<T>
            && std::copyable<T>
            && std::equality_comparable<T>
            && std::same_as<decltype(T::isActive), bool>;

    struct DefaultComponent {
        bool isActive;
        bool operator==(const DefaultComponent&) const = default;
    };
}

#endif //BENTOBOX_COMPONENT_H

#ifndef BENTOBOX_COMPONENTMANAGER_H
#define BENTOBOX_COMPONENTMANAGER_H

#include <memory>
#include "component.h"
#include "compVec.h"
#include "util/typeMap.h"


namespace {
    template<ics::Component C>
    using CompContainer = ics::CompVec<C>;

    template<ics::Component C>
    using CompContainerSize = typename CompContainer<C>::size_type;
}

class ComponentManager {
private:
    util::TypeMap components;

    template<ics::Component C>
    CompContainer<C>& getCompVec() {
        // Create the container if it does not exist
        if (!components.has<CompContainer<C>>()) {
            auto container = CompContainer<C>();
            components.insert(container);
        }

        return components.at<CompContainer<C>>();
    }
public:
    template<ics::Component C>
    auto add(const C& c) -> CompContainerSize<C> {
        auto& container = getCompVec<C>();
        return container.add(c);
    }

    template<ics::Component C>
    void remove(typename CompContainer<C>::size_type idx) {
        auto& container = getCompVec<C>();
        container.remove(idx);
    }

    template<ics::Component C>
    C& at(typename CompContainer<C>::size_type idx) {
        auto& container = getCompVec<C>();
        return container.at(idx);
    }
};

#endif //BENTOBOX_COMPONENTMANAGER_H

#ifndef BENTOBOX_ICSMANAGER_H
#define BENTOBOX_ICSMANAGER_H

#include <memory>
#include <ics/index.h>
#include <ics/component.h>
#include <ics/compVec.h>
#include <util/typeMap.h>

namespace {
    template<ics::Component C>
    using CompContainer = ics::CompVec<C>;
}

class ICSManager {
private:
    std::unique_ptr<util::TypeMap> indexes;
    std::unique_ptr<util::TypeMap> components;
public:
    template<ics::Component C>
    void addComponent(C c) {
        if (components->has<CompContainer<C>>()) {
            // The container already exists
            // TODO: test that this actually updates the container value
            auto container = components->at<CompContainer<C>>();
            container.add(c);
        } else {
            // The container does not exist
            auto container = CompContainer<C>();
            container.add(c);
            components->insert(container);
        }
    }

    template<ics::Component C, ics::Index I>
    void addIndex(I i) {
        if (indexes->has<I>()) {
            // TODO: Make a better error
            throw std::logic_error("ICSManager::addIndex: attempting to replace existing index");
        } else {
            indexes->insert(i);
        }
    }
};

#endif //BENTOBOX_ICSMANAGER_H

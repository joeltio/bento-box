#ifndef BENTOBOX_COMPONENTSTORE_H
#define BENTOBOX_COMPONENTSTORE_H

#include <unordered_map>
#include <memory>
#include <any>
#include "component.h"
#include "compVec.h"
#include "componentSet.h"

namespace ics {
    // stores size_t -> unique_ptr -> CompVec<Component>
    // stored as size_t -> unique_ptr -> any(CompVec<BaseComponent>)
    typedef std::unordered_map<size_t, std::unique_ptr<std::any>> ComponentStore;

    template<Component C>
    CompVec<C>& getCompVec(ComponentStore& store, size_t group) {
        std::any& compVecAny = *store.at(group);
        auto& compVec = std::any_cast<ics::CompVec<BaseComponent>&>(compVecAny);
        auto& castedCompVec = *reinterpret_cast<ics::CompVec<C>*>(&compVec);
        return castedCompVec;
    }

    template<Component C>
    CompVec<C>& createCompVec(ComponentStore& store, size_t group) {
        ics::CompVec<C> vec;
        ics::CompVec<BaseComponent> castedVec = *reinterpret_cast<ics::CompVec<BaseComponent>*>(&vec);

        store.emplace(
            group,
            std::make_unique<std::any>(
                std::make_any<ics::CompVec<BaseComponent>>(castedVec)
            )
        );

        return getCompVec<C>(store, group);
    }

    template<Component C>
    std::pair<size_t, size_t> addComponent(ComponentStore& store, const C& c, size_t group) {
        auto& vec = store.contains(group) ? getCompVec<C>(store, group) : createCompVec<C>(store, group);
        auto vecIndex = vec.add(c);
        return std::make_pair(group, vecIndex);
    }

    ComponentSet asCompSet(const ComponentStore& store);
}

#endif //BENTOBOX_COMPONENTSTORE_H

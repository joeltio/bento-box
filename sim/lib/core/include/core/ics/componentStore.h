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
    typedef std::unordered_map<CompGroup, std::unique_ptr<CompVec<BaseComponent>>> ComponentStore;

    template<Component C>
    CompVec<C>& getCompVec(ComponentStore& store, CompGroup group) {
        auto& compVec = *store.at(group);
        auto& castedCompVec = *reinterpret_cast<ics::CompVec<C>*>(&compVec);
        return castedCompVec;
    }

    template<Component C>
    CompVec<C>& createCompVec(ComponentStore& store, CompGroup group) {
        ics::CompVec<C> vec;
        ics::CompVec<BaseComponent> castedVec = *reinterpret_cast<ics::CompVec<BaseComponent>*>(&vec);

        store.emplace(
            group,
            std::make_unique<ics::CompVec<BaseComponent>>(castedVec)
        );

        return getCompVec<C>(store, group);
    }

    template<Component C>
    CompStoreId addComponent(ComponentStore& store, const C& c, CompGroup group) {
        auto& vec = store.contains(group) ? getCompVec<C>(store, group) : createCompVec<C>(store, group);
        auto vecIndex = vec.add(c);
        return std::make_pair(group, vecIndex);
    }

    template<Component C>
    C& getComponent(ComponentStore& store, CompStoreId compStoreId) {
        auto& vec = getCompVec<C>(store, compStoreId.first);
        return vec.at(compStoreId.second);
    }

    ComponentSet asCompSet(const ComponentStore& store);
}

#endif //BENTOBOX_COMPONENTSTORE_H

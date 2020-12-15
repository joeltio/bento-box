#ifndef BENTOBOX_COMPVEC_H
#define BENTOBOX_COMPVEC_H

#include <any>
#include <vector>
#include <queue>
#include <memory>
#include <functional>
#include <typeindex>
#include <unordered_map>
#include <iostream>

#include "component.h"

namespace ics {
    typedef unsigned long CompId;

    template<Component C>
    class CompVec {
    public:
        typedef typename std::vector<C>::size_type size_type;
    private:
        CompId lastId = 0;
        std::function<C&(std::vector<BaseComponent>* vectorPtr, size_type idx)> getter;
        std::function<const C&(const std::vector<BaseComponent>* vectorPtr, size_type idx)> constGetter;
        std::unordered_map<CompId, size_type> idToIndex;
        std::queue<size_type> inactiveCompIdx;
        std::vector<C> vec;
    protected:
        void isActiveCheck(CompId id) const;
        size_type addToVec(const C& val);
    public:
        CompVec() {
            getter = [](std::vector<BaseComponent>* vectorPtr, size_type idx) -> C& {
                auto vecPtr = reinterpret_cast<std::vector<C>*>(vectorPtr);
                return vecPtr->at(idx);
            };

            constGetter = [](const std::vector<BaseComponent>* vectorPtr, size_type idx) -> const C& {
                const auto vecPtr = reinterpret_cast<const std::vector<C>*>(vectorPtr);
                return vecPtr->at(idx);
            };
        }
        CompId add(const C& val);
        void remove(CompId id);
        size_type size();

        C& at(CompId id);
        C& operator[](CompId id);
        const C& operator[](CompId id) const;
    };

    template<Component C>
    void CompVec<C>::isActiveCheck(CompId id) const {
        auto index = idToIndex.at(id);
        const auto& comp = constGetter(reinterpret_cast<const std::vector<BaseComponent>*>(&vec), index);
        if (!comp.isActive) {
            // TODO: format the index into the string
            throw std::out_of_range("compVec::isActiveCheck: component at index is inactive");
        }
    }

    template<Component C>
    typename CompVec<C>::size_type CompVec<C>::addToVec(const C& val) {
        if (!this->inactiveCompIdx.empty()) {
            // Reuse old component space
            CompVec<C>::size_type insertIdx = this->inactiveCompIdx.front();
            this->vec.at(insertIdx) = val;
            this->inactiveCompIdx.pop();
            return insertIdx;
        } else {
            this->vec.push_back(val);
            return vec.size() - 1;
        }
    }

    template<Component C>
    CompId CompVec<C>::add(const C& val) {
        auto insertedIdx = addToVec(val);
        // Update the idToIndex map
        idToIndex.insert(std::make_pair(lastId + 1, insertedIdx));
        ++lastId;
        return lastId;
    }

    template<Component C>
    void CompVec<C>::remove(CompId id) {
        auto index = idToIndex.at(id);
        // Mark component as deleted
        auto& comp = getter(reinterpret_cast<std::vector<BaseComponent>*>(&vec), index);
        comp.isActive = false;
        // Queue the component for reuse
        inactiveCompIdx.push(index);
        // Remove the mapping from idToIdx
        idToIndex.erase(id);
    }

    template<Component C>
    typename CompVec<C>::size_type CompVec<C>::size() {
        return idToIndex.size();
    }

    template<Component C>
    C& CompVec<C>::at(CompId id) {
        isActiveCheck(id);
        auto index = idToIndex.at(id);

        return getter(reinterpret_cast<std::vector<BaseComponent>*>(&vec), index);
    }

    template<Component C>
    const C& CompVec<C>::operator[](CompId id) const {
        return this->at(id);
    }

    template<Component C>
    C& CompVec<C>::operator[](CompId id) {
        return this->at(id);
    }
}

#endif //BENTOBOX_COMPVEC_H

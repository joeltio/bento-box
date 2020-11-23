#ifndef BENTOBOX_COMPVEC_H
#define BENTOBOX_COMPVEC_H

#include <vector>
#include <queue>
#include <memory>
#include <typeindex>
#include <iostream>

#include "component.h"

namespace ics {
    template<Component C>
    class CompVec {
    public:
        typedef typename std::vector<C>::size_type size_type;
        typedef unsigned int CompId;
    private:
        CompId lastId = 0;
        std::unordered_map<CompId, size_type> idToIndex;
        std::queue<size_type> inactiveCompIdx;
        std::vector<C> vec;
    protected:
        void isActiveCheck(CompId id) const;
        size_type addToVec(const C& val);
    public:
        CompId add(const C& val);
        void remove(CompId id);

        C& at(CompId id);
        C& operator[](CompId id);
        const C& operator[](CompId id) const;
    };

    template<Component C>
    void CompVec<C>::isActiveCheck(CompId id) const {
        auto index = idToIndex.at(id);
        if (!vec.at(index).isActive) {
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
    typename CompVec<C>::CompId CompVec<C>::add(const C& val) {
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
        vec.at(index).isActive = false;
        // Queue the component for reuse
        inactiveCompIdx.push(index);
        // Remove the mapping from idToIdx
        idToIndex.erase(id);
    }

    template<Component C>
    C& CompVec<C>::at(CompId id) {
        isActiveCheck(id);
        auto index = idToIndex.at(id);
        return vec.at(index);
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

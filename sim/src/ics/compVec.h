#ifndef BENTOBOX_COMPVEC_H
#define BENTOBOX_COMPVEC_H

#include <vector>
#include <queue>
#include <memory>
#include <typeindex>

#include "component.h"

namespace ics {
    template<Component C>
    class CompVec {
    public:
        typedef typename std::vector<C>::size_type size_type;
    private:
        std::type_index initType = std::type_index(typeid(C));
        std::unique_ptr<std::queue<size_type>> inactiveCompIdx;
        std::unique_ptr<std::vector<C>> vecPtr;
    public:
        size_type add(const C& val);
        C& at(size_type idx) const;

        // Disallow assignment by operator
        C& operator[](size_type idx);
        const C& operator[](size_type idx) const;
    };

    template<Component C>
    typename CompVec<C>::size_type CompVec<C>::add(const C& val) {
        if (!this->inactiveCompIdx->empty()) {
            // Reuse old component space
            CompVec<C>::size_type insertIdx = this->inactiveCompIdx->front();
            this->vecPtr->at(insertIdx) = val;
            this->inactiveCompIdx->pop();
            return insertIdx;
        } else {
            this->vecPtr->push_back(val);
        }
    }

    template<Component C>
    C& CompVec<C>::at(CompVec<C>::size_type idx) const {
        return this->vecPtr->at(idx);
    }

    template<Component C>
    const C& CompVec<C>::operator[](size_type idx) const {
        return this->at(idx);
    }

    template<Component C>
    C& CompVec<C>::operator[](size_type idx) {
        return this->at(idx);
    }
}

#endif //BENTOBOX_COMPVEC_H

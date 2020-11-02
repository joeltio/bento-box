#include "compVec.h"

namespace ics {
    template<Component C>
    typename CompVec<C>::size_type CompVec<C>::add(const C& val) {
        if (!this->inactiveCompIdx->empty()) {
            // Reuse old component space
            CompVec<C>::size_type insertIdx = this->inactiveCompIdx->pop_front();
            this->vecPtr->at(insertIdx) = val;
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
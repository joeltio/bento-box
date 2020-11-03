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
    private:
        std::unique_ptr<std::queue<size_type>> inactiveCompIdx = std::make_unique<std::queue<size_type>>();
        std::unique_ptr<std::vector<C>> vecPtr = std::make_unique<std::vector<C>>();
    protected:
        void isActiveCheck(size_type idx) const;
    public:
        size_type add(const C& val);

        C& at(size_type idx) const;
        C& operator[](size_type idx);
        const C& operator[](size_type idx) const;

        void remove(size_type idx);
    };

    template<Component C>
    void CompVec<C>::isActiveCheck(size_type idx) const {
        if (!this->vecPtr->at(idx).isActive) {
            // TODO: format the index into the string
            throw std::out_of_range("compVec::isActiveCheck: component at index is inactive");
        }
    }

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
        this->isActiveCheck(idx);
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

    template<Component C>
    void CompVec<C>::remove(size_type idx) {
        // Mark component as deleted
        this->vecPtr->at(idx).isActive = false;
        this->inactiveCompIdx->push(idx);
    }
}

#endif //BENTOBOX_COMPVEC_H

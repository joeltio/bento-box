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
}

#endif //BENTOBOX_COMPVEC_H

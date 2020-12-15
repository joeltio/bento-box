#ifndef BENTOBOX_COMPONENTSET_H
#define BENTOBOX_COMPONENTSET_H

#include <unordered_set>
#include "compVec.h"

namespace std {
    template <> struct hash<std::pair<size_t, ics::CompId>> {
        inline size_t operator()(const std::pair<size_t, ics::CompId> &v) const {
            return v.first * 31 + v.second;
        }
    };
}

namespace ics {
    typedef std::unordered_set<std::pair<size_t, CompId>, std::hash<std::pair<size_t, CompId>>> ComponentSet;
}

#endif //BENTOBOX_COMPONENTSET_H

#ifndef BENTOBOX_COMPONENTSET_H
#define BENTOBOX_COMPONENTSET_H

#include <unordered_set>

#include "compVec.h"

namespace ics {
typedef size_t CompGroup;
typedef std::pair<CompGroup, CompId> CompStoreId;
typedef std::unordered_set<CompStoreId, std::hash<CompStoreId>> ComponentSet;
}  // namespace ics

namespace std {
// std::unordered_set does not know how to hash CompStoreId. This function
// tells C++ how to do so.
template <>
struct hash<ics::CompStoreId> {
    inline size_t operator()(const ics::CompStoreId &v) const {
        return v.first * 31 + v.second;
    }
};
}  // namespace std

#endif  // BENTOBOX_COMPONENTSET_H

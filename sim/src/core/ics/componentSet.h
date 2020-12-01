#ifndef BENTOBOX_COMPONENTSET_H
#define BENTOBOX_COMPONENTSET_H

#include <unordered_set>

namespace std {
    template <> struct hash<std::pair<size_t, size_t>> {
        inline size_t operator()(const std::pair<size_t, size_t> &v) const {
            return v.first * 31 + v.second;
        }
    };
}

namespace ics {
    typedef std::unordered_set<std::pair<size_t, size_t>, std::hash<std::pair<size_t, size_t>>> ComponentSet;
}

#endif //BENTOBOX_COMPONENTSET_H

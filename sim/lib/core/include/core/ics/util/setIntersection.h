#ifndef BENTOBOX_SET_INTERSECTION_H
#define BENTOBOX_SET_INTERSECTION_H

#include <unordered_set>

namespace util {
    // C++ does not support set intersection for unordered sets, only std::set
    // This function allows set intersection for unordered sets.
    template<class T>
    std::unordered_set<T> setIntersection(const std::unordered_set<T>& a, const std::unordered_set<T>& b) {
        std::unordered_set<T> newSet;
        for (const T& aElement : a) {
            if (b.contains(aElement)) {
                newSet.insert(aElement);
            }
        }

        return newSet;
    }
}

#endif //BENTOBOX_SET_INTERSECTION_H

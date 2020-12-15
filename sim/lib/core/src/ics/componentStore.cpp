#include <core/ics/componentStore.h>

namespace ics {
    ComponentSet asCompSet(const ComponentStore &store) {
        ComponentSet set;
        for (auto &index_ptr_pair : store) {
            auto& a = std::any_cast<CompVec<BaseComponent>&>(*index_ptr_pair.second);
            // TODO: This requires knowledge on how CompVec creates IDs. Add
            // TODO: iter functionality for compVec
            for (auto i = 1; i <= a.size(); ++i) {
                set.emplace(index_ptr_pair.first, i);
            }
        }

        return set;
    }
}

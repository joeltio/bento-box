#include <core/ics/componentStore.h>

namespace ics {
    ComponentSet asCompSet(const ComponentStore &store) {
        ComponentSet set;
        for (auto &index_ptr_pair : store) {
            auto& a = *index_ptr_pair.second;
            // TODO(joeltio): This requires knowledge on how CompVec creates IDs. Add
            // TODO(joeltio): iter functionality for compVec
            for (auto i = 1; i <= a.size(); ++i) {
                set.emplace(index_ptr_pair.first, i);
            }
        }

        return set;
    }
}

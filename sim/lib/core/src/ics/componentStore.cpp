#include <core/ics/componentStore.h>

namespace ics {
    ComponentSet asCompSet(const ComponentStore &store) {
        ComponentSet set;
        for (auto &index_ptr_pair : store) {
            auto& a = std::any_cast<CompVec<BaseComponent>&>(*index_ptr_pair.second);
            for (auto i = 0; i < a.size(); i++) {
                set.emplace(index_ptr_pair.first, i);
            }
        }

        return set;
    }
}

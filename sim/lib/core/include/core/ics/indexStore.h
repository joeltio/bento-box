#ifndef BENTOBOX_INDEXSTORE_H
#define BENTOBOX_INDEXSTORE_H

#include "util/typeMap.h"

namespace ics {
    // The indexStore stores indexes.
    // Each index contains data to retrieve components quickly. This data is
    // stored in an index object. The index object is stored altogether in this
    // index store.
    // No specific index is enforced by ICS core, hence, it is merely a map.
    typedef util::TypeMap IndexStore;
}

#endif //BENTOBOX_INDEXSTORE_H

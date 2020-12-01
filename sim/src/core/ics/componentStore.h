#ifndef BENTOBOX_COMPONENTSTORE_H
#define BENTOBOX_COMPONENTSTORE_H

#include <unordered_map>
#include <memory>
#include <any>

namespace ics {
    // size_t -> ptr -> CompVec<Component>
    typedef std::unordered_map<size_t, std::unique_ptr<std::any>> ComponentStore;
}

#endif //BENTOBOX_COMPONENTSTORE_H

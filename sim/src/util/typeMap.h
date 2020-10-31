#ifndef BENTOBOX_TYPEMAP_H
#define BENTOBOX_TYPEMAP_H

#include <unordered_map>
#include <typeindex>

namespace util {

    template<typename V>
    class typeMap {
    private:
        std::unordered_map<std::type_index, V> map;
    public:
        template<typename T> T at() {
            static_assert(
                std::is_base_of<V, T>::value,
                "Attempting to retrieve non-derived type from type map"
            );

            auto type = std::type_index(typeid(T));
            return static_cast<T>(map.at(type));
        };

        template<typename T> void insert(T value) {
            static_assert(
                std::is_base_of<V, T>::value,
                "Attempting to insert non-derived type into type map"
            );

            auto type = std::type_index(typeid(T));
            map.insert(std::make_pair(type, value));
        }
    };

}


#endif //BENTOBOX_TYPEMAP_H

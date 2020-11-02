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
        template<typename T>
        requires std::derived_from<T, V>
        T at() {
            auto type = std::type_index(typeid(T));
            return static_cast<T>(map.at(type));
        };

        template<typename T>
        requires std::derived_from<T, V>
        void insert(T value) {
            auto type = std::type_index(typeid(T));
            map.insert(std::make_pair(type, value));
        }
    };

}


#endif //BENTOBOX_TYPEMAP_H

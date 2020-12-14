#ifndef BENTOBOX_TYPEMAP_H
#define BENTOBOX_TYPEMAP_H

#include <any>
#include <unordered_map>
#include <typeindex>

namespace util {
    class TypeMap {
    private:
        std::unordered_map<std::type_index, std::any> map;
    public:
        template<typename T>
        T& at() {
            auto type = std::type_index(typeid(T));
            return std::any_cast<T&>(map.at(type));
        };

        template<typename T>
        void insert(const T& value) {
            auto type = std::type_index(typeid(T));
            map.insert(std::make_pair(type, value));
        }

        template<typename T>
        bool has() const {
            auto type = std::type_index(typeid(T));
            return map.find(type) != map.end();
        }
    };
}


#endif //BENTOBOX_TYPEMAP_H

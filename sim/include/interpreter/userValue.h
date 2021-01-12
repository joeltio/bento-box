#ifndef BENTOBOX_USERVALUE_H
#define BENTOBOX_USERVALUE_H

#include <climits>
#include <cstddef>
#include <cstdint>
#include <utility>
#include <variant>
#include <string>
#include <vector>
#include <initializer_list>

namespace interpreter {

// Assert that float is 32 bits
static_assert(sizeof(float) * CHAR_BIT == 32);
// Assert that double is 64 bits
static_assert(sizeof(double) * CHAR_BIT == 64);

typedef std::variant<std::nullptr_t, std::byte, int32_t, int64_t, float, double,
                     bool, std::string>
    UserValue;

struct UserArray {
    std::vector<size_t> dimensions;
    std::vector<UserValue> array;

    UserArray(std::vector<UserValue> array, std::vector<size_t> dimensions)
        : array(std::move(array)), dimensions(std::move(dimensions)) {}
    UserValue at(std::initializer_list<size_t> indexes);
};

}  // namespace interpreter

#endif  // BENTOBOX_USERVALUE_H

#include <stdexcept>
#include <interpreter/userValue.h>

namespace interpreter {

UserValue UserArray::at(std::initializer_list<size_t> indexes) {
    if (indexes.size() != dimensions.size()) {
        // TODO(joeltio): Add incorrect dimension sizes in error message
        throw std::out_of_range(
            "Incorrect number of index elements for retrieving one element "
            "from array");
    }

    size_t multiplier = 1;
    size_t arrayIndex = 0;
    for (std::pair i(std::rbegin(indexes), dimensions.rbegin());
         i.second != dimensions.rend(); ++i.first, ++i.second) {
        arrayIndex += multiplier * (*i.first);
        multiplier *= (*i.second);
    }

    return array.at(arrayIndex);
}

}  // namespace interpreter
#ifndef BENTOBOX_COMPOSABLE_H
#define BENTOBOX_COMPOSABLE_H

#include <concepts>
#include <variant>

namespace util {
    template<class Data>
    class Composable {
    public:
        const Data data;
        explicit Composable(Data d) : data(d) {};

        template<class Fn>
        requires std::invocable<Fn, Data>
        auto operator>=(Fn fn) -> Composable<decltype(fn(std::declval<Data>()))> {
            typedef decltype(fn(std::declval<Data>())) ReturnType;
            return Composable<ReturnType>(fn(data));
        }
    };
}

#endif //BENTOBOX_COMPOSABLE_H

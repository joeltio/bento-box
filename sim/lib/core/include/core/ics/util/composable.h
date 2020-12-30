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
        // Require that Fn is a function that has argument of type Data, i.e. Fn: (Data d) -> ??
        requires std::invocable<Fn, Data>
        // The return type is Composable<Return type of Fn(Data)>
        auto operator|(Fn fn) -> Composable<decltype(fn(std::declval<Data>()))> {
            typedef decltype(fn(std::declval<Data>())) ReturnType;
            return Composable<ReturnType>(fn(data));
        }
    };
}

#endif //BENTOBOX_COMPOSABLE_H

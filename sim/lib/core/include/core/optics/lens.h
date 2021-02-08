#ifndef BENTOBOX_LENS_H
#define BENTOBOX_LENS_H

#include <functional>

namespace optics {

template <class Return, class... Args>
class Getter {
   private:
    const std::function<Return(Args...)> getter;

   public:
    // A getter cannot be constructed without a getter function
    Getter() = delete;
    explicit Getter(std::function<Return(Args...)>&& getter) : getter(getter) {}

    Return operator()(Args&&... args) {
        return std::invoke(getter, std::forward<Args>(args)...);
    }

    template <class NewReturn>
    Getter<NewReturn, Args...> compose(
        std::function<NewReturn(Return)>&& composeGetter) {
        // Make a copy of the getter so that if the current Getter is destroyed
        // The returned getter is still usable
        std::function<Return(Args...)> getterCopy(getter);
        return Getter<NewReturn, Args...>(
            [getterCopy, composeGetter](Args... args) {
                return std::invoke(
                    composeGetter,
                    std::invoke(getterCopy, std::forward<Args>(args)...));
            });
    }

    // Oddly, C++ does not recognise lambdas when std::function is used here.
    // So, C++20 requirements are used.
    // The attempted definition of a std::function is:
    //    template<class...NewArgs>
    //    Getter<Return, NewArgs...>
    //    precompose(std::function<std::tuple_element_t<0,
    //    std::tuple<Args...>>(NewArgs...)> precomposeGetter) {
    template <class... NewArgs, class Fn>
        // Require that the current getter only needs one argument
        requires(sizeof...(Args) == 1) &&
        // Require that the type Fn is something invocable with the NewArgs and
        // returns the first argument
        std::is_invocable_r_v<
            std::tuple_element_t<0, std::tuple<Args...>>, Fn,
            NewArgs...> Getter<Return,
                               NewArgs...> precompose(Fn&& precomposeGetter) {
        // Make a copy of the getter so that if the current Getter is destroyed
        // The returned getter is still usable
        std::function<Return(Args...)> getterCopy(getter);
        return Getter<Return, NewArgs...>([getterCopy,
                                           precomposeGetter](NewArgs... args) {
            return std::invoke(
                getterCopy,
                std::invoke(precomposeGetter, std::forward<NewArgs>(args)...));
        });
    }
};

}  // namespace optics

#endif  // BENTOBOX_LENS_H

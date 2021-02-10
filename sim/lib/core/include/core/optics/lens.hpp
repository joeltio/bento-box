#ifndef BENTOBOX_LENS_HPP
#define BENTOBOX_LENS_HPP

#include <functional>
#include <type_traits>

namespace {
template <class... Args>
struct is_same_args {
    // This static constexpr function compares the given type arguments and
    // ensures that they are the same as Args
    template <size_t N = 0, class... OtherArgs>
    static constexpr bool _as() {
        // constexpr is required here because N is a non-type template
        // argument
        if constexpr (N == sizeof...(OtherArgs)) {
            return true;
        } else if (std::is_same_v<
                       std::remove_reference_t<
                           std::tuple_element_t<N, std::tuple<OtherArgs...>>>,
                       std::remove_reference_t<
                           std::tuple_element_t<N, std::tuple<Args...>>>>) {
            return _as<N + 1, OtherArgs...>();
        } else {
            return false;
        }
    }

    // Alias to the recursive comparison constexpr function
    template <class... OtherArgs>
    static constexpr bool as() {
        return _as<0, OtherArgs...>();
    }
};
}  // namespace

namespace optics {

// Note on std::move vs static_cast<std::remove_reference_t<T>&&>
// Later in the code, you will see that I have used static_cast instead of
// std::move. The reason is that we need to cast to an rvalue reference
// because that's the type of the function's parameter.
// std::move is not used because it is semantically incorrect, though it
// does the same thing.

template <class Return, class... Args>
class Getter {
   protected:
   public:
    const std::function<Return(std::remove_reference_t<Args>&&...)> getter;
    // A getter cannot be constructed without a getter function
    Getter() = delete;
    explicit Getter(std::function<Return(Args...)>&& getter)
        : getter(std::move(getter)) {}
    explicit Getter(const std::function<Return(Args...)>& getter)
        : getter(getter) {}

    template <class... RArgs>
    requires(is_same_args<Args...>::template as<RArgs...>()) Return
        get(RArgs&&... args) const {
        return getter(static_cast<std::remove_reference_t<RArgs>>(args)...);
    }

    template <class NewReturn>
    Getter<NewReturn, Args...> compose(
        std::function<NewReturn(Return)>&& composeGetter) const {
        // Make a copy of the getter so that if the current Getter is destroyed
        // The returned getter is still usable
        std::function<Return(Args...)> getterCopy(getter);
        return Getter<NewReturn, Args...>(
            [getterCopy, composeGetter](Args&&... args) {
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
                               NewArgs...> precompose(Fn&& precomposeGetter)
            const {
        // Make a copy of the getter so that if the current Getter is destroyed
        // The returned getter is still usable
        std::function<Return(Args...)> getterCopy(getter);
        return Getter<Return, NewArgs...>(
            [getterCopy, precomposeGetter](NewArgs&&... args) {
                return std::invoke(getterCopy,
                                   std::invoke(precomposeGetter,
                                               std::forward<NewArgs>(args)...));
            });
    }
};

template <class Return, class... Args>
class Lens {
   private:
    typedef std::function<void(Return&, Return&&)> SetterFn;
    // When writing the getter as a lambda, it is important to specify the
    // arguments as rvalue references and the return type as an lvalue
    // reference.
    typedef std::function<Return&(Args&&...)> GetterFn;

   public:
    const SetterFn setter;
    const GetterFn getter;
    // A lens cannot be constructed without any functions
    Lens() = delete;
    Lens(GetterFn&& getter, SetterFn&& setter)
        : getter(std::move(getter)), setter(std::move(setter)) {}
    Lens(const GetterFn& getter, const SetterFn& setter)
        : getter(getter), setter(setter) {}

    template <class... RArgs>
    requires(is_same_args<Args...>::template as<RArgs...>()) Return& get(
        RArgs&&... args) const {
        return getter(static_cast<std::remove_reference_t<RArgs>&&>(args)...);
    }

    template <class RReturn, class... RArgs>
        // Ensure that the arguments are the correct type
        requires(is_same_args<Args...>::template as<RArgs...>())
        // Ensure that RReturn is the correct type
        && std::is_same_v<std::remove_reference_t<RReturn>, Return> void set(
               RReturn&& val, RArgs&&... args) const {
        auto& ref = get(std::forward<RArgs>(args)...);
        this->setter(ref, static_cast<std::remove_reference_t<RReturn>&&>(val));
    }

    template <class NewReturn>
    Lens<NewReturn, Args...> compose(
        const Lens<NewReturn, Return>& otherLens) const {
        std::function<NewReturn&(Args && ...)> get =
            [
                getter = this->getter, otherGetter = otherLens.getter
            ]<class... PArgs>(PArgs && ... args)
                ->NewReturn& {
            return otherGetter(
                std::forward<Return>(getter(std::forward<PArgs>(args)...)));
        };

        std::function<void(NewReturn&, NewReturn &&)> set = otherLens.setter;
        return Lens<NewReturn, Args...>(get, set);
    }
};

}  // namespace optics

#endif  // BENTOBOX_LENS_HPP

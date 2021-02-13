#ifndef BENTOBOX_USERVALUE_H
#define BENTOBOX_USERVALUE_H

#include <type_traits>
#include <string>
#include <bento/protos/values.pb.h>

// Macros for template parameter packs
#define proto_NUMERIC \
    ::proto::INT32, ::proto::INT64, ::proto::FLOAT32, ::proto::FLOAT64

namespace proto {

// Type aliases for all the protobuf types
typedef int32_t INT32;
typedef int64_t INT64;
static_assert(CHAR_BIT * sizeof(float) == 32);
typedef float FLOAT32;
static_assert(CHAR_BIT * sizeof(double) == 64);
typedef double FLOAT64;
typedef std::string STR;
typedef bool BOOL;

// Concept to assert that the given type is a protobuf type
template <class T>
concept ProtobufType =
    std::is_same_v<T, INT32> || std::is_same_v<T, INT64> ||
    std::is_same_v<T, FLOAT32> || std::is_same_v<T, FLOAT64> ||
    std::is_same_v<T, STR> || std::is_same_v<T, BOOL>;

// This function is overloaded for each protobuf type. By overloading the value
// to set, we can allow C++ to deduce the type when setting a value.
// For example, C++ will deduce setVal(myVal, 30) and assume 30 is INT32, hence,
// it will run the appropriate overloaded setVal
void setVal(bento::protos::Value& protoVal, INT32 int32Val);
void setVal(bento::protos::Value& protoVal, INT64 int64Val);
void setVal(bento::protos::Value& protoVal, FLOAT32 float32Val);
void setVal(bento::protos::Value& protoVal, FLOAT64 float64Val);
void setVal(bento::protos::Value& protoVal, const std::string& strVal);
void setVal(bento::protos::Value& protoVal, const char* strVal);
void setVal(bento::protos::Value& protoVal, BOOL boolVal);

// Get value
// See the template specialisations in the .cpp file. Each specialisation deals
// with retrieving each protobuf type.
// By using template specialisations, knowing the correct type will mean that
// the correct getter is called immediately. No checks for the value's type is
// needed. For example, getVal<INT32>(val) will call val.int_32(), while
// getVal(val, int32) will require a switch case that checks through the given
// val data type.
template <class T>
// Ensure that the values are protobuf values
requires ProtobufType<T> T getVal(const bento::protos::Value& protoVal) {
    throw std::runtime_error("Invalid protobuf type.");
}

// Validate if the given protoVal is the given protobuf type.
// See the template specialisations in the .cpp file. Each specialisation deals
// with checking each protobuf type.
template <class T>
// Ensure that the values are protobuf values
requires ProtobufType<T> bool isValOfType(
    const bento::protos::Value& protoVal) {
    throw std::runtime_error("Invalid protobuf type.");
}

namespace {
// Do not export this function. Only isValOfTypes should be used.
// isValOfTypes does not have the additional N non-type template parameter
// making invocation simpler.
template <size_t N = 0, class... AllowedTypes>
requires(proto::ProtobufType<AllowedTypes>&&...) bool _isValOfTypes(
    const bento::protos::Value& val) {
    if constexpr (N == sizeof...(AllowedTypes)) {
        // Finished looping and no valid types were found
        return false;
    } else {
        // This else statement is required because the compiler seems to
        // evaluate this typedef first, which will cause an index error
        // on the iteration where the N == sizeof...(AllowedTypes)
        typedef std::tuple_element_t<N, std::tuple<AllowedTypes...>>
            CurrentType;
        // It matches one of the types
        if (proto::isValOfType<CurrentType>(val)) {
            return true;
        }

        // It doesn't match any type, recurse and get the next type
        return _isValOfTypes<N + 1, AllowedTypes...>(val);
    }
};
}  // namespace

// Validate if the given val matches one of the listed protobuf types
template <class... AllowedTypes>
// This fold expression validates that each type given is a protobuf type
requires(proto::ProtobufType<AllowedTypes>&&...) bool isValOfTypes(
    const bento::protos::Value& val) {
    return _isValOfTypes<0, AllowedTypes...>(val);
}

namespace {
template <size_t N = 0, class Type, class... TypeList>
constexpr bool _typeInTypes() {
    if constexpr (N == sizeof...(TypeList)) {
        return false;
    } else {
        typedef std::tuple_element_t<N, std::tuple<TypeList...>> CurrentType;
        if constexpr (std::is_same_v<Type, CurrentType>) {
            return true;
        }

        return _typeInTypes<N + 1, Type, TypeList...>();
    }
}
}  // namespace

// Validates if a given type is in a list of types
// For example:
// typeInTypes<int, bool, char>() == false
// typeInTypes<int, bool, char, int>() == true
// typeInTypes<std::string, bool, char, int>() == true
template <class Type, class... TypeList>
constexpr bool typeInTypes() {
    return _typeInTypes<0, Type, TypeList...>();
}

// Runs a function on the given Value after figuring out its type.
// For example, if `x` is an INT64, then, the lambda function will be called as:
// fn(x.primitive().int_64());
template <class... AllowedTypes, class Fn>
bento::protos::Value runFnWithVal(const bento::protos::Value& x, Fn fn) {
    // Validate that the given value conforms with the list of types. This is
    // done at runtime
    if (!isValOfTypes<AllowedTypes...>(x)) {
        throw std::runtime_error("Value given is not valid for this function.");
    }

    auto val = bento::protos::Value();
    bool valSet = false;
    // Each constexpr here is evaluated at compile-time. Therefore, if a
    // protobuf value is not listed list of AllowedTypes, the if statement will
    // be completely removed.
    // This is needed so that C++ doesn't flag errors for cases such as:
    // auto fn = []<class X>(X x) { return x + 2; };
    // runFnWithVal(val, fn);
    // Without removing the if statements at compile-time, C++ assumes that fn
    // may be run with getVal<STR>(x);
    // Therefore, these code paths need to be removed at compile-time so that
    // C++ knows that we will never have a case we will run fn(getVal<STR>(x))
    if constexpr (typeInTypes<INT32, AllowedTypes...>()) {
        if (isValOfType<INT32>(x)) {
            setVal(val, fn(getVal<INT32>(x)));
            valSet = true;
        }
    }
    if constexpr (typeInTypes<INT64, AllowedTypes...>()) {
        if (isValOfType<INT64>(x)) {
            setVal(val, fn(getVal<INT64>(x)));
            valSet = true;
        }
    }
    if constexpr (typeInTypes<FLOAT32, AllowedTypes...>()) {
        if (isValOfType<FLOAT32>(x)) {
            setVal(val, fn(getVal<FLOAT32>(x)));
            valSet = true;
        }
    }
    if constexpr (typeInTypes<FLOAT64, AllowedTypes...>()) {
        if (isValOfType<FLOAT64>(x)) {
            setVal(val, fn(getVal<FLOAT64>(x)));
            valSet = true;
        }
    }
    if constexpr (typeInTypes<STR, AllowedTypes...>()) {
        if (isValOfType<STR>(x)) {
            setVal(val, fn(getVal<STR>(x)));
            valSet = true;
        }
    }
    if constexpr (typeInTypes<BOOL, AllowedTypes...>()) {
        if (isValOfType<BOOL>(x)) {
            setVal(val, fn(getVal<BOOL>(x)));
            valSet = true;
        }
    }

    if (!valSet) {
        throw std::runtime_error("No value when executing function.");
    }

    return val;
}

// Runs a function on the given Value after figuring out its type.
// For example, if `x` is an INT64 and `y` is FLOAT32, then, the lambda function
// will be called as:
// fn(x.primitive().int_64(), y.primitive().float_32());
template <class... AllowedTypes, class Fn>
bento::protos::Value runFnWithVal(const bento::protos::Value& x,
                                  const bento::protos::Value& y, Fn fn) {
    auto val = bento::protos::Value();
    // We need to deduce two types here. We use our existing function which
    // deduces one type and run it twice.
    runFnWithVal<AllowedTypes...>(x, [&val, &y, fn]<class X>(X x) {
        // At this point, we have deduced the type of x. Now, we run the
        // function again to deduce the type of y
        val = runFnWithVal<AllowedTypes...>(y, [&x, fn]<class Y>(Y y) {
            // Now, we have deduced the type of x and y. We call the function
            // with both.
            return fn(x, y);
        });

        // The return value of this lambda is supposed to be some protobuf
        // primitive type e.g. 20. However, we only have the final Value.
        // Here, I return a dummy value but I have set the external scope's
        // `val` to the final value.
        return 3;
    });

    return val;
}

}  // namespace proto

#endif  // BENTOBOX_USERVALUE_H

#ifndef BENTOBOX_USERVALUE_H
#define BENTOBOX_USERVALUE_H

#include <type_traits>
#include <string>
#include <bento/protos/values.pb.h>

// Macros for template parameter packs
#define proto_NUMERIC ::proto::INT32, ::proto::INT64, ::proto::FLOAT32, ::proto::FLOAT64

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

// Overloads for setting a value
void setVal(bento::protos::Value& protoVal, INT32 int32Val);
void setVal(bento::protos::Value& protoVal, INT64 int64Val);
void setVal(bento::protos::Value& protoVal, FLOAT32 float32Val);
void setVal(bento::protos::Value& protoVal, FLOAT64 float64Val);
void setVal(bento::protos::Value& protoVal, const std::string& strVal);
void setVal(bento::protos::Value& protoVal, const char* strVal);
void setVal(bento::protos::Value& protoVal, BOOL boolVal);

// Get value
template <class T>
// Ensure that the values are protobuf values
requires ProtobufType<T> T getVal(const bento::protos::Value& protoVal) {
    throw std::runtime_error("Invalid protobuf type.");
}

// Check value type
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

template <class... AllowedTypes>
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

template <class Type, class... TypeList>
constexpr bool typeInTypes() {
    return _typeInTypes<0, Type, TypeList...>();
}

template <class... AllowedTypes, class Fn>
bento::protos::Value runFnWithVal(const bento::protos::Value& x, Fn fn) {
    if (!isValOfTypes<AllowedTypes...>(x)) {
        throw std::runtime_error("Value given is not valid for this function.");
    }

    auto val = bento::protos::Value();
    bool valSet = false;
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

template <class... AllowedTypes, class Fn>
bento::protos::Value runFnWithVal(const bento::protos::Value& x,
                                  const bento::protos::Value& y, Fn fn) {
    auto val = bento::protos::Value();
    runFnWithVal<AllowedTypes...>(x, [&val, &y, fn]<class X>(X x) {
        // The return value of the lambda is supposed to be some protobuf
        // primitive type. However, what we need is just the proto::Value, so
        // just return anything here and extract the value by setting it by
        // reference
        val = runFnWithVal<AllowedTypes...>(
            y, [&x, fn]<class Y>(Y y) { return fn(x, y); });
        return 3;
    });

    return val;
}

}  // namespace interpreter

#endif  // BENTOBOX_USERVALUE_H

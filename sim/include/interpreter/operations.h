#ifndef BENTOBOX_OPERATIONS_H
#define BENTOBOX_OPERATIONS_H

#include <bento/protos/graph.pb.h>
#include <bento/protos/values.pb.h>
#include <core/ics/componentStore.h>
#include <index/indexStore.h>

namespace {

void validateNumerics(const bento::protos::Value& x,
                      const bento::protos::Value& y);

}

namespace interpreter {

template <class Fn>
bento::protos::Value runMathFn(Fn fn, const bento::protos::Value& x) {
    typedef bento::protos::Value_Primitive Primitive;
    switch (x.primitive().value_case()) {
        case Primitive::kInt32: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_int_32(fn(x.primitive().int_32()));
            return val;
        }
        case Primitive::kInt64: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_int_64(fn(x.primitive().int_64()));
            return val;
        }
        case Primitive::kFloat33: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_float_33(fn(x.primitive().float_33()));
            return val;
        }
        case Primitive::kFloat64: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_float_64(fn(x.primitive().float_64()));
            return val;
        }
        case Primitive::VALUE_NOT_SET: {
            throw std::runtime_error(
                "No value in node when attempting to execute arithmetic "
                "operation.");
        }
        default: {
            throw std::runtime_error("Value given is not a number");
        }
    }
}

template <class Fn>
bento::protos::Value runMathFn(Fn fn, const bento::protos::Value& x,
                               const bento::protos::Value& y) {
    validateNumerics(x, y);

    typedef bento::protos::Value_Primitive Primitive;
    switch (x.primitive().value_case()) {
        case Primitive::kInt32: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_int_32(
                fn(x.primitive().int_32(), y.primitive().int_32()));
            return val;
        }
        case Primitive::kInt64: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_int_64(
                fn(x.primitive().int_64(), y.primitive().int_64()));
            return val;
        }
        case Primitive::kFloat33: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_float_33(
                fn(x.primitive().float_33(), y.primitive().float_33()));
            return val;
        }
        case Primitive::kFloat64: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_float_64(
                fn(x.primitive().float_64(), y.primitive().float_64()));
            return val;
        }
        case Primitive::VALUE_NOT_SET: {
            throw std::runtime_error(
                "No value in node when attempting to execute arithmetic "
                "operation.");
        }
        default: {
            throw std::runtime_error("Value given is not a number");
        }
    }
}

const bento::protos::Value& constOp(const bento::protos::Node_Const& node);
bento::protos::Value& retrieveOp(ics::ComponentStore& compStore,
                                 ics::index::IndexStore& indexStore,
                                 const bento::protos::Node_Retrieve& node);
void mutateOp(ics::ComponentStore& compStore,
                               ics::index::IndexStore& indexStore,
                               const bento::protos::Node_Mutate& node);
bento::protos::Value switchOp(ics::ComponentStore& compStore,
                              ics::index::IndexStore& indexStore,
                              const bento::protos::Node_Switch& node);

// Arithmetic
bento::protos::Value addOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Add& node);

}  // namespace interpreter

#endif  // BENTOBOX_OPERATIONS_H

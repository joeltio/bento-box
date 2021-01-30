#ifndef BENTOBOX_OPERATIONS_H
#define BENTOBOX_OPERATIONS_H

#include <bento/protos/graph.pb.h>
#include <bento/protos/values.pb.h>
#include <core/ics/componentStore.h>
#include <index/indexStore.h>

namespace {

void validateSame(const bento::protos::Value_Primitive& x,
                  const bento::protos::Value_Primitive& y);
void validateSame(const bento::protos::Value_Array& x,
                  const bento::protos::Value_Array& y);
void validateSame(const bento::protos::Value& x, const bento::protos::Value& y);

void validateNumeric(const bento::protos::Value_Primitive& x);

void validateBoolean(const bento::protos::Value_Primitive& x);

}  // namespace

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
        case Primitive::kFloat32: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_float_32(fn(x.primitive().float_32()));
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
    validateSame(x, y);
    validateNumeric(x.primitive());

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
        case Primitive::kFloat32: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_float_32(
                fn(x.primitive().float_32(), y.primitive().float_32()));
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

template <class Fn>
bento::protos::Value runBoolFn(Fn fn, const bento::protos::Value& x) {
    typedef bento::protos::Value_Primitive Primitive;
    switch (x.primitive().value_case()) {
        case Primitive::kInt32: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_boolean(fn(x.primitive().int_32()));
            return val;
        }
        case Primitive::kInt64: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_boolean(fn(x.primitive().int_64()));
            return val;
        }
        case Primitive::kFloat32: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_boolean(fn(x.primitive().float_32()));
            return val;
        }
        case Primitive::kFloat64: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_boolean(fn(x.primitive().float_64()));
            return val;
        }
        case Primitive::kBoolean: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_boolean(fn(x.primitive().boolean()));
            return val;
        }
        case Primitive::kStrVal: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_boolean(fn(x.primitive().str_val()));
            return val;
        }
        case Primitive::VALUE_NOT_SET: {
            throw std::runtime_error(
                "No value in node when attempting to execute boolean "
                "operation.");
        }
    }
}

template <class Fn>
bento::protos::Value runBoolFn(Fn fn, const bento::protos::Value& x,
                               const bento::protos::Value& y) {
    validateSame(x, y);

    typedef bento::protos::Value_Primitive Primitive;
    switch (x.primitive().value_case()) {
        case Primitive::kInt32: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_boolean(
                fn(x.primitive().int_32(), y.primitive().int_32()));
            return val;
        }
        case Primitive::kInt64: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_boolean(
                fn(x.primitive().int_64(), y.primitive().int_64()));
            return val;
        }
        case Primitive::kFloat32: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_boolean(
                fn(x.primitive().float_32(), y.primitive().float_32()));
            return val;
        }
        case Primitive::kFloat64: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_boolean(
                fn(x.primitive().float_64(), y.primitive().float_64()));
            return val;
        }
        case Primitive::kBoolean: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_boolean(
                fn(x.primitive().boolean(), y.primitive().boolean()));
            return val;
        }
        case Primitive::kStrVal: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_boolean(
                fn(x.primitive().str_val(), y.primitive().str_val()));
            return val;
        }
        case Primitive::VALUE_NOT_SET: {
            throw std::runtime_error(
                "No value in node when attempting to execute boolean "
                "operation.");
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
bento::protos::Value subOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Sub& node);
bento::protos::Value mulOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Mul& node);
bento::protos::Value divOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Div& node);
bento::protos::Value maxOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Max& node);
bento::protos::Value minOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Min& node);
bento::protos::Value absOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Abs& node);
bento::protos::Value floorOp(ics::ComponentStore& compStore,
                             ics::index::IndexStore& indexStore,
                             const bento::protos::Node_Floor& node);
bento::protos::Value ceilOp(ics::ComponentStore& compStore,
                            ics::index::IndexStore& indexStore,
                            const bento::protos::Node_Ceil& node);
bento::protos::Value powOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Pow& node);
bento::protos::Value modOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Mod& node);
bento::protos::Value sinOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Sin& node);
bento::protos::Value arcSinOp(ics::ComponentStore& compStore,
                              ics::index::IndexStore& indexStore,
                              const bento::protos::Node_ArcSin& node);
bento::protos::Value cosOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Cos& node);
bento::protos::Value arcCosOp(ics::ComponentStore& compStore,
                              ics::index::IndexStore& indexStore,
                              const bento::protos::Node_ArcCos& node);
bento::protos::Value tanOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Tan& node);
bento::protos::Value arcTanOp(ics::ComponentStore& compStore,
                              ics::index::IndexStore& indexStore,
                              const bento::protos::Node_ArcTan& node);

// Random number generation
bento::protos::Value randomOp(ics::ComponentStore& compStore,
                              ics::index::IndexStore& indexStore,
                              const bento::protos::Node_Random& node);

// Boolean operations
bento::protos::Value andOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_And& node);
bento::protos::Value orOp(ics::ComponentStore& compStore,
                          ics::index::IndexStore& indexStore,
                          const bento::protos::Node_Or& node);
bento::protos::Value notOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Not& node);

// Checks for equivalence of values (floating point rounding errors will not be
// corrected)
bento::protos::Value eqOp(ics::ComponentStore& compStore,
                          ics::index::IndexStore& indexStore,
                          const bento::protos::Node_Eq& node);
bento::protos::Value gtOp(ics::ComponentStore& compStore,
                          ics::index::IndexStore& indexStore,
                          const bento::protos::Node_Gt& node);
bento::protos::Value ltOp(ics::ComponentStore& compStore,
                          ics::index::IndexStore& indexStore,
                          const bento::protos::Node_Lt& node);
bento::protos::Value geOp(ics::ComponentStore& compStore,
                          ics::index::IndexStore& indexStore,
                          const bento::protos::Node_Ge& node);
bento::protos::Value leOp(ics::ComponentStore& compStore,
                          ics::index::IndexStore& indexStore,
                          const bento::protos::Node_Le& node);

}  // namespace interpreter

#endif  // BENTOBOX_OPERATIONS_H

#include <interpreter/operations.h>
#include <interpreter/graphInterpreter.h>
#include <ics.h>
#include <cmath>

namespace {

void validateNumerics(const bento::protos::Value& x,
                      const bento::protos::Value& y) {
    // Ensure that they are primitives
    if (!x.has_primitive() || !y.has_primitive()) {
        throw std::runtime_error("Numeric values must be primitive.");
    }

    // Ensure that they are the same type
    if (x.primitive().value_case() != y.primitive().value_case()) {
        throw std::runtime_error(
            "Values to perform arithmetic on must be the same type.");
    }
}

}  // namespace

namespace interpreter {

const bento::protos::Value& constOp(const bento::protos::Node_Const& node) {
    return node.held_value();
}

bento::protos::Value& retrieveOp(ics::ComponentStore& compStore,
                                 ics::index::IndexStore& indexStore,
                                 const bento::protos::Node_Retrieve& node) {
    // Get the AttributeRef
    auto& ref = node.retrieve_attr();
    // Retrieve the component
    auto& component = ics::getComponent(indexStore, compStore, ref.component(),
                                        ref.entity_id());
    // Get the attribute of the component
    return component.getMutableValue(ref.attribute());
}

void mutateOp(ics::ComponentStore& compStore,
              ics::index::IndexStore& indexStore,
              const bento::protos::Node_Mutate& node) {
    // Get the new value to set
    auto val = evaluateNode(compStore, indexStore, node.to_node());

    // Get a reference to the value to modify
    auto& ref = node.mutate_attr();
    auto& component = ics::getComponent(indexStore, compStore, ref.component(),
                                        ref.entity_id());
    auto& mutableVal = component.getMutableValue(ref.attribute());

    // Set the value
    component.setValue(ref.attribute(), val);
}

bento::protos::Value switchOp(ics::ComponentStore& compStore,
                              ics::index::IndexStore& indexStore,
                              const bento::protos::Node_Switch& node) {
    auto conditionVal =
        evaluateNode(compStore, indexStore, node.condition_node());
    // Ensure that the value returned is a boolean
    if (!conditionVal.has_primitive() ||
        conditionVal.primitive().value_case() !=
            bento::protos::Value::Primitive::kBoolean) {
        throw std::runtime_error(
            "Value returned from condition node is not a boolean.");
    }

    if (conditionVal.primitive().boolean()) {
        return evaluateNode(compStore, indexStore, node.true_node());
    } else {
        return evaluateNode(compStore, indexStore, node.false_node());
    }
}

bento::protos::Value addOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Add& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());
    auto op = []<class C>(C x, C y) { return x + y; };
    return runMathFn(op, xVal, yVal);
}

bento::protos::Value subOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Sub& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());
    auto op = []<class C>(C x, C y) { return x - y; };
    return runMathFn(op, xVal, yVal);
}

bento::protos::Value mulOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Mul& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());
    auto op = []<class C>(C x, C y) { return x * y; };
    return runMathFn(op, xVal, yVal);
}

bento::protos::Value divOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Div& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());
    auto op = []<class C>(C x, C y) { return x / y; };
    return runMathFn(op, xVal, yVal);
}

bento::protos::Value maxOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Max& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());
    auto op = []<class C>(C x, C y) {
        if (x > y) {
            return x;
        } else {
            return y;
        }
    };
    return runMathFn(op, xVal, yVal);
}

bento::protos::Value minOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Min& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());
    auto op = []<class C>(C x, C y) {
        if (x < y) {
            return x;
        } else {
            return y;
        }
    };
    return runMathFn(op, xVal, yVal);
}

bento::protos::Value absOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Abs& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto op = []<class C>(C x) { return abs(x); };
    return runMathFn(op, xVal);
}

bento::protos::Value floorOp(ics::ComponentStore& compStore,
                             ics::index::IndexStore& indexStore,
                             const bento::protos::Node_Floor& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto op = []<class C>(C x) { return floor(x); };
    return runMathFn(op, xVal);
}

bento::protos::Value ceilOp(ics::ComponentStore& compStore,
                            ics::index::IndexStore& indexStore,
                            const bento::protos::Node_Ceil& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto op = []<class C>(C x) { return ceil(x); };
    return runMathFn(op, xVal);
}

bento::protos::Value powOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Pow& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());
    auto op = []<class C>(C x, C y) { return pow(x, y); };
    return runMathFn(op, xVal, yVal);
}

bento::protos::Value modOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Mod& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());

    // Only integers can use modulo, so write the switch case here manually
    // This code is taken from runMathFn
    validateNumerics(xVal, yVal);

    typedef bento::protos::Value_Primitive Primitive;
    switch (xVal.primitive().value_case()) {
        case Primitive::kInt32: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_int_32(xVal.primitive().int_32() %
                                                yVal.primitive().int_32());
            return val;
        }
        case Primitive::kInt64: {
            auto val = bento::protos::Value();
            val.mutable_primitive()->set_int_64(xVal.primitive().int_64() %
                                                yVal.primitive().int_64());
            return val;
        }
        default:
            throw std::runtime_error(
                "Cannot perform modulo operation on non-integral values.");
    }
}

}  // namespace interpreter
#include <interpreter/operations.h>
#include <interpreter/graphInterpreter.h>
#include <ics.h>
#include <cmath>
#include <random>

namespace {

void validateSame(const bento::protos::Value_Primitive& x,
                  const bento::protos::Value_Primitive& y) {
    if (x.value_case() != y.value_case()) {
        throw std::runtime_error("Primitive values must be the same type.");
    }
}

void validateSame(const bento::protos::Value_Array& x,
                  const bento::protos::Value_Array& y) {
    if (x.values_size() != y.values_size()) {
        throw std::runtime_error("Arrays must have the same size.");
    }

    for (size_t i = 0; i < x.values_size(); i++) {
        auto& xPrimitive = x.values(i);
        auto& yPrimitive = y.values(i);

        validateSame(xPrimitive, yPrimitive);
    }
}

void validateSame(const bento::protos::Value& x,
                  const bento::protos::Value& y) {
    if (x.kind_case() != y.kind_case()) {
        throw std::runtime_error("Values must be the same type.");
    }

    // x and y are primitives
    if (x.has_primitive()) {
        validateSame(x.primitive(), y.primitive());
        return;
    }

    validateSame(x.array(), y.array());
}

void validateNumeric(const bento::protos::Value_Primitive& x) {
    typedef bento::protos::Value_Primitive Primitive;
    switch (x.value_case()) {
        case Primitive::kInt32:
        case Primitive::kInt64:
        case Primitive::kFloat32:
        case Primitive::kFloat64:
            return;
        case Primitive::VALUE_NOT_SET: {
            throw std::runtime_error("No value when validating numeric value.");
        }
        default: {
            throw std::runtime_error("Value given is not numeric.");
        }
    }
}

void validateBoolean(const bento::protos::Value_Primitive& x) {
    typedef bento::protos::Value_Primitive Primitive;
    switch (x.value_case()) {
        case Primitive::kBoolean:
            return;
        case Primitive::VALUE_NOT_SET: {
            throw std::runtime_error("No value when validating boolean value.");
        }
        default: {
            throw std::runtime_error("Value given is not a boolean.");
        }
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
    validateSame(xVal, yVal);
    validateNumeric(xVal.primitive());

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

bento::protos::Value sinOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Sin& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto op = []<class C>(C x) { return sin(x); };
    return runMathFn(op, xVal);
}

bento::protos::Value arcSinOp(ics::ComponentStore& compStore,
                              ics::index::IndexStore& indexStore,
                              const bento::protos::Node_ArcSin& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto op = []<class C>(C x) {
        if (x < -1 || x > 1) {
            throw std::domain_error("arcSin's valid domain is [-1, 1].");
        }
        return asin(x);
    };
    return runMathFn(op, xVal);
}

bento::protos::Value cosOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Cos& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto op = []<class C>(C x) { return cos(x); };
    return runMathFn(op, xVal);
}

bento::protos::Value arcCosOp(ics::ComponentStore& compStore,
                              ics::index::IndexStore& indexStore,
                              const bento::protos::Node_ArcCos& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto op = []<class C>(C x) {
        if (x < -1 || x > 1) {
            throw std::domain_error("arcCos's valid domain is [-1, 1].");
        }
        return acos(x);
    };
    return runMathFn(op, xVal);
}

bento::protos::Value tanOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Tan& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto op = []<class C>(C x) { return tan(x); };
    return runMathFn(op, xVal);
}

bento::protos::Value arcTanOp(ics::ComponentStore& compStore,
                              ics::index::IndexStore& indexStore,
                              const bento::protos::Node_ArcTan& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto op = []<class C>(C x) { return atan(x); };
    return runMathFn(op, xVal);
}

// Generate random number
bento::protos::Value randomOp(ics::ComponentStore& compStore,
                              ics::index::IndexStore& indexStore,
                              const bento::protos::Node_Random& node) {
    // Create random device and generator
    static std::random_device rd;
    static std::mt19937 gen(rd());

    auto lowVal = evaluateNode(compStore, indexStore, node.low());
    auto highVal = evaluateNode(compStore, indexStore, node.high());

    // Lambdas cannot capture static variables, so the code from runMathFn is
    // put here.
    validateSame(lowVal, highVal);
    validateNumeric(lowVal.primitive());

    auto& lowPrimitive = lowVal.primitive();
    auto& highPrimitive = highVal.primitive();

    auto val = bento::protos::Value();

    typedef bento::protos::Value_Primitive Primitive;
    switch (lowPrimitive.value_case()) {
        case Primitive::kFloat32: {
            auto dist = std::uniform_real_distribution(
                lowPrimitive.float_32(), highPrimitive.float_32());
            val.mutable_primitive()->set_float_32(dist(gen));
            return val;
        }
        case Primitive::kFloat64: {
            auto dist = std::uniform_real_distribution(
                lowPrimitive.float_64(), highPrimitive.float_64());
            val.mutable_primitive()->set_float_64(dist(gen));
            return val;
        }
        case Primitive::VALUE_NOT_SET: {
            throw std::runtime_error(
                "No value in node when attempting to execute arithmetic "
                "operation.");
        }
        default: {
            throw std::runtime_error(
                "Random op requires floating point bounds.");
        }
    }
}

bento::protos::Value andOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_And& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());

    validateSame(xVal, yVal);
    validateBoolean(xVal.primitive());

    auto val = bento::protos::Value();
    val.mutable_primitive()->set_boolean(xVal.primitive().boolean() and
                                         yVal.primitive().boolean());
    val.mutable_data_type()->set_primitive(bento::protos::Type_Primitive_BOOL);

    return val;
}

bento::protos::Value orOp(ics::ComponentStore& compStore,
                          ics::index::IndexStore& indexStore,
                          const bento::protos::Node_Or& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());

    validateSame(xVal, yVal);
    validateBoolean(xVal.primitive());

    auto val = bento::protos::Value();
    val.mutable_primitive()->set_boolean(xVal.primitive().boolean() or
                                         yVal.primitive().boolean());
    val.mutable_data_type()->set_primitive(bento::protos::Type_Primitive_BOOL);

    return val;
}

bento::protos::Value notOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Not& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());

    validateBoolean(xVal.primitive());

    auto val = bento::protos::Value();
    val.mutable_primitive()->set_boolean(!xVal.primitive().boolean());
    val.mutable_data_type()->set_primitive(bento::protos::Type_Primitive_BOOL);

    return val;
}

bento::protos::Value eqOp(ics::ComponentStore& compStore,
                          ics::index::IndexStore& indexStore,
                          const bento::protos::Node_Eq& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());

    validateSame(xVal, yVal);

    auto op = []<class C>(C x, C y) { return x == y; };

    return runBoolFn(op, xVal, yVal);
}

bento::protos::Value gtOp(ics::ComponentStore& compStore,
                          ics::index::IndexStore& indexStore,
                          const bento::protos::Node_Gt& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());

    validateSame(xVal, yVal);
    validateNumeric(xVal.primitive());

    auto op = []<class C>(C x, C y) { return x > y; };

    return runBoolFn(op, xVal, yVal);
}

bento::protos::Value ltOp(ics::ComponentStore& compStore,
                          ics::index::IndexStore& indexStore,
                          const bento::protos::Node_Lt& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());

    validateSame(xVal, yVal);
    validateNumeric(xVal.primitive());

    auto op = []<class C>(C x, C y) { return x < y; };

    return runBoolFn(op, xVal, yVal);
}

bento::protos::Value geOp(ics::ComponentStore& compStore,
                          ics::index::IndexStore& indexStore,
                          const bento::protos::Node_Ge& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());

    validateSame(xVal, yVal);
    validateNumeric(xVal.primitive());

    auto op = []<class C>(C x, C y) { return x >= y; };

    return runBoolFn(op, xVal, yVal);
}

bento::protos::Value leOp(ics::ComponentStore& compStore,
                          ics::index::IndexStore& indexStore,
                          const bento::protos::Node_Le& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());

    validateSame(xVal, yVal);
    validateNumeric(xVal.primitive());

    auto op = []<class C>(C x, C y) { return x <= y; };

    return runBoolFn(op, xVal, yVal);
}

}  // namespace interpreter
#include <interpreter/operations.h>
#include <interpreter/graphInterpreter.h>
#include <proto/userValue.h>
#include <ics.h>
#include <cmath>
#include <random>

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
    auto op = []<class X, class Y>(X x, Y y) { return x + y; };
    return proto::runFnWithVal<proto_NUMERIC>(xVal, yVal, op);
}

bento::protos::Value subOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Sub& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());
    auto op = []<class X, class Y>(X x, Y y) { return x - y; };
    return proto::runFnWithVal<proto_NUMERIC>(xVal, yVal, op);
}

bento::protos::Value mulOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Mul& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());
    auto op = []<class X, class Y>(X x, Y y) { return x * y; };
    return proto::runFnWithVal<proto_NUMERIC>(xVal, yVal, op);
}

bento::protos::Value divOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Div& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());
    auto op = []<class X, class Y>(X x, Y y) { return x / y; };
    return proto::runFnWithVal<proto_NUMERIC>(xVal, yVal, op);
}

bento::protos::Value maxOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Max& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());
    auto op = []<class X, class Y>(X x, Y y) {
        typedef decltype(std::declval<X>() + std::declval<Y>()) RetType;
        if (x > y) {
            return (RetType)x;
        } else {
            return (RetType)y;
        }
    };
    return proto::runFnWithVal<proto_NUMERIC>(xVal, yVal, op);
}

bento::protos::Value minOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Min& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());
    auto op = []<class X, class Y>(X x, Y y) {
        typedef decltype(std::declval<X>() + std::declval<Y>()) RetType;
        if (x < y) {
            return (RetType)x;
        } else {
            return (RetType)y;
        }
    };
    return proto::runFnWithVal<proto_NUMERIC>(xVal, yVal, op);
}

bento::protos::Value absOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Abs& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto op = []<class C>(C x) { return abs(x); };
    return proto::runFnWithVal<proto_NUMERIC>(xVal, op);
}

bento::protos::Value floorOp(ics::ComponentStore& compStore,
                             ics::index::IndexStore& indexStore,
                             const bento::protos::Node_Floor& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto op = []<class C>(C x) { return floor(x); };
    return proto::runFnWithVal<proto_NUMERIC>(xVal, op);
}

bento::protos::Value ceilOp(ics::ComponentStore& compStore,
                            ics::index::IndexStore& indexStore,
                            const bento::protos::Node_Ceil& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto op = []<class C>(C x) { return ceil(x); };
    return proto::runFnWithVal<proto_NUMERIC>(xVal, op);
}

bento::protos::Value powOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Pow& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());
    auto op = []<class X, class Y>(X x, Y y) { return pow(x, y); };
    return proto::runFnWithVal<proto_NUMERIC>(xVal, yVal, op);
}

bento::protos::Value modOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Mod& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());

    auto op = []<class X, class Y>(X x, Y y) { return x % y; };
    return proto::runFnWithVal<proto::INT32, proto::INT64>(xVal, yVal, op);
}

bento::protos::Value sinOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Sin& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto op = []<class C>(C x) { return sin(x); };
    return proto::runFnWithVal<proto_NUMERIC>(xVal, op);
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
    return proto::runFnWithVal<proto_NUMERIC>(xVal, op);
}

bento::protos::Value cosOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Cos& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto op = []<class C>(C x) { return cos(x); };
    return proto::runFnWithVal<proto_NUMERIC>(xVal, op);
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
    return proto::runFnWithVal<proto_NUMERIC>(xVal, op);
}

bento::protos::Value tanOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_Tan& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto op = []<class C>(C x) { return tan(x); };
    return proto::runFnWithVal<proto_NUMERIC>(xVal, op);
}

bento::protos::Value arcTanOp(ics::ComponentStore& compStore,
                              ics::index::IndexStore& indexStore,
                              const bento::protos::Node_ArcTan& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto op = []<class C>(C x) { return atan(x); };
    return proto::runFnWithVal<proto_NUMERIC>(xVal, op);
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

    auto op = []<class X, class Y>(X low, Y high) {
        typedef decltype(std::declval<X>() + std::declval<Y>()) CombinedType;
        auto dist = std::uniform_real_distribution(
            static_cast<CombinedType>(low), static_cast<CombinedType>(high));
        return dist(gen);
    };
    return proto::runFnWithVal<proto::FLOAT32, proto::FLOAT64>(lowVal, highVal,
                                                               op);
}

bento::protos::Value andOp(ics::ComponentStore& compStore,
                           ics::index::IndexStore& indexStore,
                           const bento::protos::Node_And& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());

    if (!proto::isValOfType<proto::BOOL>(xVal) ||
        !proto::isValOfType<proto::BOOL>(yVal)) {
        throw std::domain_error(
            "Cannot run AND operation on non-boolean values.");
    }

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

    if (!proto::isValOfType<proto::BOOL>(xVal) ||
        !proto::isValOfType<proto::BOOL>(yVal)) {
        throw std::domain_error(
            "Cannot run OR operation on non-boolean values.");
    }

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

    if (!proto::isValOfType<proto::BOOL>(xVal)) {
        throw std::domain_error(
            "Cannot run NOT operation on non-boolean values.");
    }

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

    auto op = []<class X, class Y>(X x, Y y) { return x == y; };
    if (proto::isValOfTypes<proto_NUMERIC>(xVal)) {
        // Run the function with other possible numeric comparisons
        return proto::runFnWithVal<proto_NUMERIC>(xVal, yVal, op);
    } else if (proto::isValOfType<proto::STR>(xVal)) {
        // Run the function with only string values allowed
        return proto::runFnWithVal<proto::STR>(xVal, yVal, op);
    } else if (proto::isValOfType<proto::BOOL>(xVal)) {
        return proto::runFnWithVal<proto::BOOL>(xVal, yVal, op);
    } else {
        throw std::domain_error(
            "Checking equivalence between given values is not possible.");
    }
}

bento::protos::Value gtOp(ics::ComponentStore& compStore,
                          ics::index::IndexStore& indexStore,
                          const bento::protos::Node_Gt& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());

    auto op = []<class X, class Y>(X x, Y y) { return x > y; };
    return proto::runFnWithVal<proto_NUMERIC>(xVal, yVal, op);
}

bento::protos::Value ltOp(ics::ComponentStore& compStore,
                          ics::index::IndexStore& indexStore,
                          const bento::protos::Node_Lt& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());

    auto op = []<class X, class Y>(X x, Y y) { return x < y; };
    return proto::runFnWithVal<proto_NUMERIC>(xVal, yVal, op);
}

bento::protos::Value geOp(ics::ComponentStore& compStore,
                          ics::index::IndexStore& indexStore,
                          const bento::protos::Node_Ge& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());

    auto op = []<class X, class Y>(X x, Y y) { return x >= y; };
    return proto::runFnWithVal<proto_NUMERIC>(xVal, yVal, op);
}

bento::protos::Value leOp(ics::ComponentStore& compStore,
                          ics::index::IndexStore& indexStore,
                          const bento::protos::Node_Le& node) {
    auto xVal = evaluateNode(compStore, indexStore, node.x());
    auto yVal = evaluateNode(compStore, indexStore, node.y());

    auto op = []<class X, class Y>(X x, Y y) { return x <= y; };
    return proto::runFnWithVal<proto_NUMERIC>(xVal, yVal, op);
}

}  // namespace interpreter
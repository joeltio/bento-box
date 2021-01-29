#include <interpreter/operations.h>
#include <ics.h>
#include <interpreter/graphInterpreter.h>

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

}

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
    // Get the attribute name of the component
    return component.getMutableValue(ref.attribute());
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
    auto op = []<class C>(C x, C y){
        return x + y;
    };
    return runMathFn(op, xVal, yVal);
}

}  // namespace interpreter
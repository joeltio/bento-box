#include <interpreter/graphInterpreter.h>
#include <interpreter/operations.h>
#include <ics.h>

namespace interpreter {

bento::protos::Value evaluateNode(ics::ComponentStore& compStore,
                                  ics::index::IndexStore& indexStore,
                                  const bento::protos::Node& node) {
    typedef bento::protos::Node::OpCase OpCase;
    typedef bento::protos::Value Value;
    switch (node.op_case()) {
        case OpCase::kConstOp:
            return constOp(node.const_op());
        case OpCase::kRetrieveOp:
            return retrieveOp(compStore, indexStore, node.retrieve_op());
        case OpCase::kMutateOp:
            throw std::logic_error(
                "Node to evaluate should not modify any attribute.");
        case OpCase::kSwitchOp:
            return switchOp(compStore, indexStore, node.switch_op());
        case OpCase::kAddOp:
            return addOp(compStore, indexStore, node.add_op());
        case OpCase::kSubOp:
            return subOp(compStore, indexStore, node.sub_op());
        case OpCase::kMulOp:
            return mulOp(compStore, indexStore, node.mul_op());
        case OpCase::kDivOp:
            return divOp(compStore, indexStore, node.div_op());
        case OpCase::kMaxOp:
            return maxOp(compStore, indexStore, node.max_op());
        case OpCase::kMinOp:
            return minOp(compStore, indexStore, node.min_op());
        case OpCase::kAbsOp:
            return absOp(compStore, indexStore, node.abs_op());
        case OpCase::kFloorOp:
            return floorOp(compStore, indexStore, node.floor_op());
        case OpCase::kCeilOp:
            return ceilOp(compStore, indexStore, node.ceil_op());
        case OpCase::kPowOp:
            return powOp(compStore, indexStore, node.pow_op());
        case OpCase::kModOp:
            return modOp(compStore, indexStore, node.mod_op());
        case OpCase::kSinOp:
        case OpCase::kArcsinOp:
        case OpCase::kCosOp:
        case OpCase::kArccosOp:
        case OpCase::kTanOp:
        case OpCase::kArctanOp:
        case OpCase::kRandomOp:
        case OpCase::kAndOp:
        case OpCase::kOrOp:
        case OpCase::kNotOp:
        case OpCase::kEqOp:
        case OpCase::kGtOp:
        case OpCase::kLtOp:
        case OpCase::kGeOp:
        case OpCase::kLeOp:
        default:
            throw std::domain_error("Unknown case when parsing OpCase.");
    }
}

void runGraph(const bento::protos::Graph& graph, ics::ComponentStore& compStore,
              ics::index::IndexStore& indexStore) {
    // Evaluate inputs
    for (const auto& output : graph.outputs()) {
        mutateOp(compStore, indexStore, output);
    }
}

}  // namespace interpreter
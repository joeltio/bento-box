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
            return sinOp(compStore, indexStore, node.sin_op());
        case OpCase::kArcsinOp:
            return arcSinOp(compStore, indexStore, node.arcsin_op());
        case OpCase::kCosOp:
            return cosOp(compStore, indexStore, node.cos_op());
        case OpCase::kArccosOp:
            return arcCosOp(compStore, indexStore, node.arccos_op());
        case OpCase::kTanOp:
            return tanOp(compStore, indexStore, node.tan_op());
        case OpCase::kArctanOp:
            return arcTanOp(compStore, indexStore, node.arctan_op());
        case OpCase::kRandomOp:
            return randomOp(compStore, indexStore, node.random_op());
        case OpCase::kAndOp:
            return andOp(compStore, indexStore, node.and_op());
        case OpCase::kOrOp:
            return orOp(compStore, indexStore, node.or_op());
        case OpCase::kNotOp:
            return notOp(compStore, indexStore, node.not_op());
        case OpCase::kEqOp:
            return eqOp(compStore, indexStore, node.eq_op());
        case OpCase::kGtOp:
            return gtOp(compStore, indexStore, node.gt_op());
        case OpCase::kLtOp:
            return ltOp(compStore, indexStore, node.lt_op());
        case OpCase::kGeOp:
            return geOp(compStore, indexStore, node.ge_op());
        case OpCase::kLeOp:
            return leOp(compStore, indexStore, node.le_op());
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
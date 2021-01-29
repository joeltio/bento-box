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
        case OpCase::kConstOp: {
            return constOp(node.const_op());
        }
        case OpCase::kRetrieveOp: {
            return retrieveOp(compStore, indexStore, node.retrieve_op());
        }
        case OpCase::kMutateOp: {
            throw std::logic_error(
                "Node to evaluate should not modify any attribute.");
        }
        case OpCase::kSwitchOp: {
            return switchOp(compStore, indexStore, node.switch_op());
        }
        case OpCase::kAddOp: {
            return addOp(compStore, indexStore, node.add_op());
        }
        case OpCase::kSubOp:
        case OpCase::kMulOp:
        case OpCase::kDivOp:
        case OpCase::kMaxOp:
        case OpCase::kMinOp:
        case OpCase::kAbsOp:
        case OpCase::kFloorOp:
        case OpCase::kCeilOp:
        case OpCase::kPowOp:
        case OpCase::kModOp:
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
//        auto& ref =
//            getAttributeRef(compStore, indexStore, output.mutate_attr());
        //        output.target_node() ref = evalNode(output.to_node());
    }
}

}  // namespace interpreter
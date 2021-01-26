#include <graphInterpreter.h>
#include <ics.h>

bento::protos::Value& getAttributeRef(const bento::protos::AttributeRef& ref,
                                      ics::ComponentStore& compStore,
                                      ics::index::IndexStore& indexStore) {
    // Retrieve the component
    auto& component = ics::getComponent(indexStore, compStore, ref.component(),
                                        ref.entity_id());
    // Get the attribute name of the component
    return component.getMutableValue(ref.attribute());
}

void runGraph(const bento::protos::Graph& graph, ics::ComponentStore& compStore,
              ics::index::IndexStore& indexStore) {
    // Evaluate inputs
    for (const auto& output : graph.outputs()) {
        auto& ref =
            getAttributeRef(output.mutate_attr(), compStore, indexStore);
        //        output.target_node() ref = evalNode(output.to_node());
    }
}

#ifndef BENTOBOX_GRAPHINTERPRETER_H
#define BENTOBOX_GRAPHINTERPRETER_H

#include <bento/protos/graph.pb.h>
#include <core/ics/componentStore.h>
#include <index/indexStore.h>

namespace interpreter {

bento::protos::Value evaluateNode(ics::ComponentStore& compStore,
                                  ics::index::IndexStore& indexStore,
                                  const bento::protos::Node& node);

void runGraph(ics::ComponentStore& compStore,
              ics::index::IndexStore& indexStore,
              const bento::protos::Graph& graph);

}  // namespace interpreter

#endif  // BENTOBOX_GRAPHINTERPRETER_H

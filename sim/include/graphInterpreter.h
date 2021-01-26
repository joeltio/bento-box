#ifndef BENTOBOX_GRAPHINTERPRETER_H
#define BENTOBOX_GRAPHINTERPRETER_H

#include <bento/protos/graph.pb.h>
#include <core/ics/componentStore.h>
#include <index/indexStore.h>

bento::protos::Value& getAttributeRef(const bento::protos::AttributeRef& ref,
                                      ics::ComponentStore& compStore,
                                      ics::index::IndexStore& indexStore);

void runGraph(const bento::protos::Graph& graph,
              const ics::ComponentStore& compStore,
              const ics::index::IndexStore& indexStore);

#endif  // BENTOBOX_GRAPHINTERPRETER_H

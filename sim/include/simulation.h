#ifndef BENTOBOX_SIMULATION_H
#define BENTOBOX_SIMULATION_H

#include <bento/protos/sim.pb.h>
#include <core/ics/componentStore.h>
#include <index/indexStore.h>

#include <utility>

struct Simulation {
    bento::protos::SimulationDef simDef;
    ics::ComponentStore compStore;
    ics::index::IndexStore indexStore;

    explicit Simulation(bento::protos::SimulationDef simDef)
        : simDef(std::move(simDef)) {}
};

#endif  // BENTOBOX_SIMULATION_H

#ifndef BENTOBOX_SIMULATION_H
#define BENTOBOX_SIMULATION_H

#include <bento/protos/sim.pb.h>
#include <core/ics/componentStore.h>
#include <index/indexStore.h>

#include <utility>

struct Simulation {
    // Value that indicates that the entity ID is unset
    // An entity ID will be generated if the entity ID is set to this value
    static const ::google::protobuf::uint32 UNSET_ENTITY_ID = 0;
    bento::protos::SimulationDef simDef;
    ics::ComponentStore compStore;
    ics::index::IndexStore indexStore;

    explicit Simulation(bento::protos::SimulationDef simDef)
        : simDef(std::move(simDef)) {
        // BE CAREFUL: Once simDef is moved into this->simDef, all references to
        // simDef are invalid. Always use this->simDef
        for (size_t i=0; i < this->simDef.entities_size(); i++) {
            if (this->simDef.entities(i).id() == UNSET_ENTITY_ID) {
                ::google::protobuf::uint32 entityId;
                do {
                    entityId = indexStore.entity.addEntityId();
                } while (entityId == UNSET_ENTITY_ID);

                this->simDef.mutable_entities(i)->set_id(entityId);
            }
        }
    }
};

#endif  // BENTOBOX_SIMULATION_H

#ifndef BENTOBOX_SIMULATION_H
#define BENTOBOX_SIMULATION_H

#include <bento/protos/sim.pb.h>
#include <core/ics/componentStore.h>
#include <index/indexStore.h>
#include <forward_list>
#include <ics.h>

#include <utility>

struct Simulation {
    // Value that indicates that the entity ID is unset
    // An entity ID will be generated if the entity ID is set to this value
    static const ::google::protobuf::uint32 UNSET_ENTITY_ID = 0;
    static const ::google::protobuf::uint32 UNSET_SYSTEM_ID = 0;
    bento::protos::SimulationDef simDef;
    ics::ComponentStore compStore;
    ics::index::IndexStore indexStore;
    // The simulation will be locked when it has started
    // No changes should be made to the simDef when it is locked
    bool locked = false;

    explicit Simulation(bento::protos::SimulationDef simDef)
        : simDef(std::move(simDef)) {
        // BE CAREFUL: Once simDef is moved into this->simDef, all references to
        // simDef are invalid. Always use this->simDef

        // Create a map from component name to component def for use later
        std::unordered_map<std::string, bento::protos::ComponentDef> compDefMap;
        for (size_t i = 0; i < this->simDef.components_size(); i++) {
            compDefMap[this->simDef.components(i).name()] =
                this->simDef.components(i);
        }

        // Retrieve all the existing entity IDs to configure the indexStore
        std::forward_list<ics::index::EntityIndex::EntityId> configuredIds;
        for (size_t i = 0; i < this->simDef.entities_size(); i++) {
            auto& entity = this->simDef.entities(i);
            if (entity.id() != UNSET_ENTITY_ID) {
                configuredIds.push_front(entity.id());
            }
        }

        // Configure the indexStore with the existing entity IDs
        indexStore.entity.setEntityIds(configuredIds);

        // Create the components and entity IDs (if needed) for all entities
        for (size_t i = 0; i < this->simDef.entities_size(); i++) {
            auto& entity = this->simDef.entities(i);
            // If the entity ID is unset, create one and set it
            if (entity.id() == UNSET_ENTITY_ID) {
                ::google::protobuf::uint32 entityId;
                do {
                    entityId = indexStore.entity.addEntityId();
                } while (entityId == UNSET_ENTITY_ID);

                this->simDef.mutable_entities(i)->set_id(entityId);
            }

            // Create the entity's components
            for (size_t j = 0; j < entity.components_size(); j++) {
                const auto& compName = entity.components(j);
                auto comp = ics::component::UserComponent(compName,
                                                          compDefMap[compName]);
                auto compStoreId =
                    ics::addComponent(indexStore, compStore, comp);
                indexStore.entity.addComponent(entity.id(), compStoreId);
            }
        }

        // Retrieve all the existing system IDs to avoid
        uint32_t maxId = 0;
        for (size_t i = 0; i < this->simDef.systems_size(); i++) {
            auto& system = this->simDef.systems(i);
            if (system.id() != UNSET_SYSTEM_ID && system.id() > maxId) {
                maxId = system.id();
            }
        }

        // Set the system IDs of the rest of the systems
        for (size_t i = 0; i < this->simDef.systems_size(); i++) {
            auto& system = this->simDef.systems(i);
            // If the system ID is unset, create one and set it
            if (system.id() == UNSET_SYSTEM_ID) {
                maxId++;
                this->simDef.mutable_systems(i)->set_id(maxId);
            }
        }
    }
};

#endif  // BENTOBOX_SIMULATION_H

/*
 * bentobox-sim
 * Engine gRPC Service
 */

#include "git.h"
#include "service/engineService.h"
#include <sstream>
#include <interpreter/graphInterpreter.h>
#include <interpreter/operations.h>

using grpc::ServerContext;
using grpc::Status;

namespace service {

/** Format an error message with the given message and exception **/
std::string formatError(const std::string& message, const std::exception& e) {
    std::ostringstream err;
    err << message << ": " << e.what();
    return err.str();
}

Status EngineServiceImpl::GetVersion(
    ServerContext* context, const bento::protos::GetVersionReq* request,
    bento::protos::GetVersionResp* response) {
    response->set_commit_hash(GIT_HASH);
    return Status::OK;
}

Status EngineServiceImpl::ApplySimulation(
    grpc::ServerContext* context,
    const bento::protos::ApplySimulationReq* request,
    bento::protos::ApplySimulationResp* response) {
    // Overrides/Creates a new simulation
    auto name = request->simulation().name();

    if (sims.contains(name) && sims[name]->locked) {
        return Status(
            grpc::ALREADY_EXISTS,
            "The simulation has been created and stepped at least once.");
    }

    try {
        sims[name] =
            std::make_unique<Simulation>(Simulation(request->simulation()));
    } catch (const std::exception& e) {
        return Status(
            grpc::INTERNAL,
            formatError(
                "Something went wrong while creating the simulation object",
                e));
    }

    try {
        // If no init_graph is set, the default graph given by protobuf does
        // nothing, so no checks are needed here for the existence of init_graph
        interpreter::runGraph(sims[name]->compStore, sims[name]->indexStore,
                              sims[name]->simDef.init_graph());
    } catch (const std::exception& e) {
        return Status(
            grpc::INTERNAL,
            formatError("Something went wrong while running the initGraph of "
                        "the simulation",
                        e));
    }

    response->mutable_simulation()->CopyFrom(sims[name]->simDef);

    return Status::OK;
}

Status EngineServiceImpl::GetSimulation(
    ServerContext* context, const bento::protos::GetSimulationReq* request,
    bento::protos::GetSimulationResp* response) {
    // Return an error if there is no such simulation
    if (!sims.contains(request->name())) {
        return Status(grpc::NOT_FOUND,
                      "Could not find simulation with that name.");
    }

    auto& sim = *sims.at(request->name());
    response->mutable_simulation()->CopyFrom(sim.simDef);

    return Status::OK;
}

Status EngineServiceImpl::ListSimulation(
    ServerContext* context, const bento::protos::ListSimulationReq* request,
    bento::protos::ListSimulationResp* response) {
    // mutable_sim_names needs to be called so that protobuf knows that it has
    // been defined, regardless of whether there are names
    auto simNames = response->mutable_sim_names();

    for (const auto& pair : sims) {
        // Make a copy of the string and add it in
        simNames->Add(std::string(pair.first));
    }

    return Status::OK;
}

Status EngineServiceImpl::DropSimulation(
    ServerContext* context, const bento::protos::DropSimulationReq* request,
    bento::protos::DropSimulationResp* response) {
    if (!sims.contains(request->name())) {
        return Status(grpc::NOT_FOUND,
                      "Could not find simulation with that name.");
    }

    sims.erase(request->name());
    return Status::OK;
}

Status EngineServiceImpl::StepSimulation(
    ServerContext* context, const bento::protos::StepSimulationReq* request,
    bento::protos::StepSimulationResp* response) {
    if (!sims.contains(request->name())) {
        return Status(grpc::NOT_FOUND,
                      "Could not find simulation with that name.");
    }

    auto& sim = sims.at(request->name());

    // TODO: Run built-in systems as well
    auto& indexStore = sim->indexStore;
    auto& compStore = sim->compStore;
    auto& simDef = sim->simDef;

    // Lock the simulation
    if (!sim->locked) {
        sim->locked = true;
    }

    for (size_t i = 0; i < simDef.systems_size(); i++) {
        const auto& graph = simDef.systems(i).graph();

        try {
            interpreter::runGraph(compStore, indexStore, graph);
        } catch (const std::exception& e) {
            return Status(
                grpc::INTERNAL,
                formatError(
                    "Something went wrong while running system with ID: " +
                        std::to_string(i) + ".",
                    e));
        }
    }

    return Status::OK;
}

Status EngineServiceImpl::GetAttribute(
    ServerContext* context, const bento::protos::GetAttributeReq* request,
    bento::protos::GetAttributeResp* response) {
    if (!sims.contains(request->sim_name())) {
        return Status(grpc::NOT_FOUND,
                      "Could not find simulation with that name.");
    }

    auto& indexStore = sims.at(request->sim_name())->indexStore;
    auto& compStore = sims.at(request->sim_name())->compStore;
    auto& simDef = sims.at(request->sim_name())->simDef;

    // Use interpreter's operations to find the attribute for consistency
    // Create the retrieve node
    auto retrieveNode = bento::protos::Node_Retrieve();
    retrieveNode.mutable_retrieve_attr()->CopyFrom(request->attribute());

    try {
        auto val = interpreter::retrieveOp(compStore, indexStore, retrieveNode);
        // CopyFrom does not accept rvalue references, so there is no speed-up
        // from moving
        response->mutable_value()->CopyFrom(val);
    } catch (const std::exception& e) {
        // It is fair to assume that retrieveOp will only throw errors because
        // the data could not be found
        return Status(
            grpc::NOT_FOUND,
            formatError(
                "RetrieveOp failed when retrieving requested attribute.", e));
    }

    return Status::OK;
}

Status EngineServiceImpl::SetAttribute(
    ServerContext* context, const bento::protos::SetAttributeReq* request,
    bento::protos::SetAttributeResp* response) {
    if (!sims.contains(request->sim_name())) {
        return Status(grpc::NOT_FOUND,
                      "Could not find simulation with that name.");
    }

    auto& indexStore = sims.at(request->sim_name())->indexStore;
    auto& compStore = sims.at(request->sim_name())->compStore;
    auto& simDef = sims.at(request->sim_name())->simDef;

    // Use interpreter's node to find the attribute for consistency
    // Create a const node holding the value
    auto valConstNode = bento::protos::Node();
    valConstNode.mutable_const_op()->mutable_held_value()->CopyFrom(
        request->value());
    // Create the retrieve node
    auto mutateNode = bento::protos::Node_Mutate();
    mutateNode.mutable_mutate_attr()->CopyFrom(request->attribute());
    mutateNode.mutable_to_node()->CopyFrom(valConstNode);

    try {
        interpreter::mutateOp(compStore, indexStore, mutateNode);
    } catch (const std::exception& e) {
        // We can't be sure whether there was something wrong with evaluating
        // the node to set or retrieving attributes failed
        return Status(grpc::INTERNAL,
                      formatError("Setting attribute failed.", e));
    }

    return Status::OK;
}

}  // namespace service

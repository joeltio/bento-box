/*
 * bentobox-sim
 * Engine gRPC Service
 */

#include "git.h"
#include "service/engineService.h"
#include <interpreter/graphInterpreter.h>
#include <interpreter/operations.h>

using grpc::ServerContext;
using grpc::Status;

namespace service {

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

    sims[name] =
        std::make_unique<Simulation>(Simulation(request->simulation()));

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
        interpreter::runGraph(compStore, indexStore, sim->simDef.init_graph());
    }

    for (size_t i = 0; i < simDef.systems_size(); i++) {
        const auto& graph = simDef.systems(i).graph();
        interpreter::runGraph(compStore, indexStore, graph);
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

    auto val = interpreter::retrieveOp(compStore, indexStore, retrieveNode);
    // CopyFrom does not accept rvalue references, so there is no speed-up from
    // moving
    response->mutable_value()->CopyFrom(val);

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

    interpreter::mutateOp(compStore, indexStore, mutateNode);

    return Status::OK;
}

}  // namespace service

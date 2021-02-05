#ifndef ENGINESERVICEIMPL_H
#define ENGINESERVICEIMPL_H
/*
 * bentobox-sim
 * Engine gRPC Service
 */

#include "bento/protos/services.grpc.pb.h"
#include <simulation.h>

namespace service {
class EngineServiceImpl final : public bento::protos::EngineService::Service {
   private:
    // simulation name -> simulation ptr
    std::unordered_map<std::string, std::unique_ptr<Simulation>> sims;

   public:
    // See services.proto for documentation on service calls
    grpc::Status GetVersion(grpc::ServerContext* context,
                            const bento::protos::GetVersionReq* request,
                            bento::protos::GetVersionResp* response) override;

    grpc::Status ApplySimulation(
        grpc::ServerContext* context,
        const bento::protos::ApplySimulationReq* request,
        bento::protos::ApplySimulationResp* response) override;
    grpc::Status GetSimulation(
        grpc::ServerContext* context,
        const bento::protos::GetSimulationReq* request,
        bento::protos::GetSimulationResp* response) override;
    grpc::Status ListSimulation(
        grpc::ServerContext* context,
        const bento::protos::ListSimulationReq* request,
        bento::protos::ListSimulationResp* response) override;
    grpc::Status DropSimulation(
        grpc::ServerContext* context,
        const bento::protos::DropSimulationReq* request,
        bento::protos::DropSimulationResp* response) override;

    grpc::Status StepSimulation(
        grpc::ServerContext* context,
        const bento::protos::StepSimulationReq* request,
        bento::protos::StepSimulationResp* response) override;

    grpc::Status GetAttribute(
        grpc::ServerContext* context,
        const bento::protos::GetAttributeReq* request,
        bento::protos::GetAttributeResp* response) override;
    grpc::Status SetAttribute(
        grpc::ServerContext* context,
        const bento::protos::SetAttributeReq* request,
        bento::protos::SetAttributeResp* response) override;
};
}  // namespace service

#endif /* ifndef ENGINESERVICEIMPL_H */

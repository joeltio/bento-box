#ifndef ENGINESERVICEIMPL_H
#define ENGINESERVICEIMPL_H
/*
 * bentobox-sim
 * Engine gRPC Service
 */

#include "bento/protos/services.grpc.pb.h"

namespace service {
class EngineServiceImpl final : public bento::protos::EngineService::Service {
   public:
    // See services.proto for documentation on service calls
    grpc::Status GetVersion(grpc::ServerContext *context,
                            const bento::protos::GetVersionReq *request,
                            bento::protos::GetVersionResp *response) override;
};
}  // namespace service

#endif /* ifndef ENGINESERVICEIMPL_H */

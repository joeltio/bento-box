#ifndef ENGINESERVICEIMPL_H
#define ENGINESERVICEIMPL_H value
/*
 * bentobox-sim
 * Engine gRPC Service
 */

#include <bento/protos/services.grpc.pb.h>

class EngineServiceImpl final : public bento::protos::EngineService::Service {
   public:
    EngineServiceImpl();

    /** Get version information about the engine */
    grpc::Status GetVersion(grpc::ServerContext *context,
                            const bento::protos::GetVersionReq *request,
                            bento::protos::GetVersionResp *response) override;
};

#endif /* ifndef ENGINESERVICEIMPL_H */

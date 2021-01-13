/*
 * bentobox-sim
 * Engine gRPC Service
 */

#include "git.h"
#include "service/engineService.h"

using bento::protos::GetVersionReq;
using bento::protos::GetVersionResp;
using grpc::ServerContext;
using grpc::Status;

Status EngineServiceImpl::GetVersion(ServerContext *context,
                                     const GetVersionReq *request,
                                     GetVersionResp *response) {
    response->set_commit_hash(GIT_HASH);
    return Status::OK;
}

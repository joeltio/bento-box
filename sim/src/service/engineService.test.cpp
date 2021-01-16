/*
 * bentobox-sim
 * Engine gRPC Service tests
 */

#include <gtest/gtest.h>
#include <grpc++/grpc++.h>

#include "git.h"
#include "network/grpcServer.h"
#include "service/engineService.h"

#define TEST_SUITE EngineServiceImpl
#define TEST_PORT 54243

using bento::protos::EngineService;
using bento::protos::GetVersionReq;
using bento::protos::GetVersionResp;
using grpc::ClientContext;
using grpc::CreateChannel;
using grpc::InsecureChannelCredentials;
using grpc::Service;
using grpc::Status;
using network::GRPCServer;
using service::EngineServiceImpl;
using std::list;
using std::make_shared;
using std::make_unique;
using std::move;
using std::pair;
using std::string;
using std::to_string;
using std::unique_ptr;

// creates test fixtures for engine service tests
class EngineServiceTest : public testing::Test {
   protected:
    // test gRPC server running engine service
    unique_ptr<GRPCServer> server;
    unique_ptr<EngineService::Stub> client;
    unique_ptr<EngineServiceImpl> engineSvc;

    EngineServiceTest() {
        // setup test server serving engine
        engineSvc = make_unique<EngineServiceImpl>();
        list<Service *> services = {engineSvc.get()};
        server = make_unique<GRPCServer>("localhost", TEST_PORT, services);
        string address = "localhost:" + to_string(TEST_PORT);

        // setup test client that talks to the test server
        auto channel = CreateChannel(address, InsecureChannelCredentials());
        client = move(EngineService::NewStub(channel));
    }
};

TEST_F(EngineServiceTest, GetVersion) {
    GetVersionReq versionReq;
    GetVersionResp versionResp;
    ClientContext context;
    Status s = client->GetVersion(&context, versionReq, &versionResp);
    ASSERT_TRUE(s.ok());
    ASSERT_EQ(versionResp.commit_hash(), GIT_HASH);
}

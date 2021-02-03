/*
 * bentobox-sim
 * Engine gRPC Service tests
 */

#include <gtest/gtest.h>
#include <grpc++/grpc++.h>

#include "git.h"
#include <network/grpcServer.h>
#include <service/engineService.h>
#include <test_simulation.h>
#include <simulation.h>

#define TEST_SUITE EngineServiceImpl
#define TEST_PORT 54243

using namespace bento::protos;
using namespace network;
using namespace service;
using grpc::ClientContext;
using grpc::Status;

// creates test fixtures for engine service tests
class EngineServiceTest : public testing::Test {
   protected:
    // test gRPC server running engine service
    std::unique_ptr<GRPCServer> server;
    std::unique_ptr<EngineService::Stub> client;
    std::unique_ptr<EngineServiceImpl> engineSvc;

    EngineServiceTest() {
        // setup test server serving engine
        engineSvc = std::make_unique<EngineServiceImpl>();
        std::list<grpc::Service*> services = {engineSvc.get()};
        server = std::make_unique<GRPCServer>("localhost", TEST_PORT, services);
        std::string address = "localhost:" + std::to_string(TEST_PORT);

        // setup test client that talks to the test server
        auto channel =
            CreateChannel(address, grpc::InsecureChannelCredentials());
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

TEST_F(EngineServiceTest, ApplyAndGetSimDef) {
    ApplySimulationReq applyReq;
    ApplySimulationResp applyResp;
    ClientContext applyContext;

    auto simDef = test_simulation::testSimDef();
    applyReq.mutable_simulation()->CopyFrom(simDef);

    // Execute ApplySimulation
    Status s = client->ApplySimulation(&applyContext, applyReq, &applyResp);
    ASSERT_TRUE(s.ok());

    GetSimulationReq getReq;
    GetSimulationResp getResp;
    ClientContext getContext;
    getReq.set_name(simDef.name());
    client->GetSimulation(&getContext, getReq, &getResp);
    // For some reason, protobuf doesn't implement equality on its message
    // objects
    ASSERT_EQ(getResp.simulation().components_size(), simDef.components_size());
    ASSERT_EQ(getResp.simulation().entities_size(), simDef.entities_size());
}

TEST_F(EngineServiceTest, ApplyCreatesEntities) {
    ApplySimulationReq applyReq;
    ApplySimulationResp applyResp;
    ClientContext applyContext;

    // Create comp def
    auto compDef = test_simulation::TestComponent().compDef;

    // Create entity def
    auto entityDef = bento::protos::EntityDef();
    auto unsetEntityId = Simulation::UNSET_ENTITY_ID;
    entityDef.mutable_components()->Add(std::string(compDef.name()));
    entityDef.set_id(unsetEntityId);

    // Create sim def
    auto simDef = bento::protos::SimulationDef();
    simDef.set_name("test simulation");
    simDef.mutable_components()->Add(std::move(compDef));
    simDef.mutable_entities()->Add(std::move(entityDef));
    applyReq.mutable_simulation()->CopyFrom(simDef);

    // Execute ApplySimulation
    Status s = client->ApplySimulation(&applyContext, applyReq, &applyResp);
    ASSERT_TRUE(s.ok());

    GetSimulationReq getReq;
    GetSimulationResp getResp;
    ClientContext getContext;
    getReq.set_name(simDef.name());
    client->GetSimulation(&getContext, getReq, &getResp);
    const auto& createdSimDef = getResp.simulation();
    ASSERT_NE(createdSimDef.entities(0).id(), unsetEntityId);
}

TEST_F(EngineServiceTest, ListSims) {
    // Start with no simulations
    ListSimulationReq listReq;
    ListSimulationResp listResp;
    ClientContext list1Context;
    Status listStatus =
        client->ListSimulation(&list1Context, listReq, &listResp);
    ASSERT_TRUE(listStatus.ok());
    ASSERT_EQ(listResp.sim_names_size(), 0);

    // Apply a sim
    ApplySimulationReq applyReq;
    ApplySimulationResp applyResp;
    ClientContext applyContext;

    auto simDef = test_simulation::testSimDef();
    applyReq.mutable_simulation()->CopyFrom(simDef);

    // Execute ApplySimulation
    Status applyStatus =
        client->ApplySimulation(&applyContext, applyReq, &applyResp);
    ASSERT_TRUE(applyStatus.ok());

    // Ensure the new sim is listed
    listReq = ListSimulationReq();
    listResp = ListSimulationResp();
    // Cannot reassign context variable, so use a new variable
    ClientContext list2Context;
    client->ListSimulation(&list2Context, listReq, &listResp);
    ASSERT_TRUE(listStatus.ok());
    ASSERT_EQ(listResp.sim_names_size(), 1);
    ASSERT_EQ(listResp.sim_names(0), simDef.name());
}

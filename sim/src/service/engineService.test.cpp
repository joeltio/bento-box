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

    ApplySimulationResp applySim(const bento::protos::SimulationDef& simDef) {
        ApplySimulationReq req;
        ApplySimulationResp resp;
        ClientContext context;
        req.mutable_simulation()->CopyFrom(simDef);
        Status s = client->ApplySimulation(&context, req, &resp);
        if (!s.ok()) {
            throw std::runtime_error(s.error_message());
        }

        return resp;
    }

    ListSimulationResp listSims() {
        ListSimulationReq req;
        ListSimulationResp resp;
        ClientContext context;
        Status s = client->ListSimulation(&context, req, &resp);
        if (!s.ok()) {
            throw std::runtime_error(s.error_message());
        }

        return resp;
    }

    GetSimulationResp getSim(const char* name) {
        GetSimulationReq req;
        GetSimulationResp resp;
        ClientContext context;
        req.set_name(name);
        Status s = client->GetSimulation(&context, req, &resp);
        if (!s.ok()) {
            throw std::runtime_error(s.error_message());
        }

        return resp;
    }

    GetAttributeResp getAttr(const char* simName,
                             const bento::protos::AttributeRef& attrRef) {
        GetAttributeReq req;
        GetAttributeResp resp;
        ClientContext context;
        req.set_sim_name(simName);
        req.mutable_attribute()->CopyFrom(attrRef);
        Status s = client->GetAttribute(&context, req, &resp);
        if (!s.ok()) {
            throw std::runtime_error(s.error_message());
        }

        return resp;
    }

    void setAttr(const char* simName,
                 const bento::protos::AttributeRef& attrRef,
                 const bento::protos::Value& val) {
        SetAttributeReq req;
        SetAttributeResp resp;
        ClientContext context;
        req.set_sim_name(simName);
        req.mutable_attribute()->CopyFrom(attrRef);
        req.mutable_value()->CopyFrom(val);
        Status s = client->SetAttribute(&context, req, &resp);
        if (!s.ok()) {
            throw std::runtime_error(s.error_message());
        }
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
    auto testSim = test_simulation::TestSimulation();
    const auto& simDef = testSim.simDef;
    auto applyResp = applySim(testSim.simDef);

    // For some reason, protobuf doesn't implement equality on its message
    // objects
    ASSERT_EQ(applyResp.simulation().components_size(),
              simDef.components_size());
    ASSERT_EQ(applyResp.simulation().entities_size(), simDef.entities_size());
}

TEST_F(EngineServiceTest, ApplyCreatesEntities) {
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

    // Apply the sim
    applySim(simDef);

    auto getResp = getSim(simDef.name().c_str());
    const auto& createdSimDef = getResp.simulation();
    ASSERT_NE(createdSimDef.entities(0).id(), unsetEntityId);
}

TEST_F(EngineServiceTest, ListSims) {
    Status s;
    // Start with no simulations
    auto listResp = listSims();
    ASSERT_EQ(listResp.sim_names_size(), 0);

    // Apply a sim
    auto testSim = test_simulation::TestSimulation();
    applySim(testSim.simDef);

    // Ensure the new sim is listed
    listResp = listSims();
    ASSERT_EQ(listResp.sim_names_size(), 1);
    ASSERT_EQ(listResp.sim_names(0), testSim.SIM_NAME);
}

TEST_F(EngineServiceTest, DropSim) {
    // Apply a sim
    auto testSim = test_simulation::TestSimulation();
    applySim(testSim.simDef);

    // Start with no simulations
    auto listResp = listSims();
    ASSERT_EQ(listResp.sim_names_size(), 1);

    // Drop the sim
    DropSimulationReq dropReq;
    DropSimulationResp dropResp;
    ClientContext dropContext;
    dropReq.set_name(testSim.SIM_NAME);
    Status s = client->DropSimulation(&dropContext, dropReq, &dropResp);
    ASSERT_TRUE(s.ok());

    listResp = listSims();
    ASSERT_EQ(listResp.sim_names_size(), 0);
}

TEST_F(EngineServiceTest, StepSim) {
    // Apply a sim
    auto testSim = test_simulation::TestSimulation();
    applySim(testSim.simDef);

    // Step the sim
    StepSimulationReq stepReq;
    StepSimulationResp stepResp;
    ClientContext stepContext;
    stepReq.set_name(testSim.SIM_NAME);
    Status s = client->StepSimulation(&stepContext, stepReq, &stepResp);
    ASSERT_TRUE(s.ok());

    // Retrieve the height attribute
    GetAttributeReq getReq;
    GetAttributeResp getResp;
    ClientContext getContext;
    getReq.set_sim_name(testSim.SIM_NAME);
    getReq.mutable_attribute()->CopyFrom(interpreter::createAttrRef(
        test_simulation::TEST_COMPONENT_NAME, 1, "height"));
    s = client->GetAttribute(&getContext, getReq, &getResp);
    ASSERT_TRUE(s.ok());

    ASSERT_EQ(getResp.value().primitive().int_64(), 1);
}

TEST_F(EngineServiceTest, StepSimLocksSim) {
    // Apply a sim
    auto testSim = test_simulation::TestSimulation();
    applySim(testSim.simDef);

    // Step the sim
    StepSimulationReq stepReq;
    StepSimulationResp stepResp;
    ClientContext stepContext;
    stepReq.set_name(testSim.SIM_NAME);
    Status s = client->StepSimulation(&stepContext, stepReq, &stepResp);
    ASSERT_TRUE(s.ok());

    // Reapply sim
    EXPECT_ANY_THROW(applySim(testSim.simDef));
}

TEST_F(EngineServiceTest, GetAndSetAttribute) {
    // Apply a sim
    auto testSim = test_simulation::TestSimulation();
    applySim(testSim.simDef);

    // Step the sim so that init graph is executed
    StepSimulationReq stepReq;
    StepSimulationResp stepResp;
    ClientContext stepContext;
    stepReq.set_name(testSim.SIM_NAME);
    Status s = client->StepSimulation(&stepContext, stepReq, &stepResp);
    ASSERT_TRUE(s.ok());

    // Get the height attribute
    auto attr = interpreter::createAttrRef(testSim.compDef.name().c_str(),
                                           testSim.entityDef.id(), "height");
    auto resp = getAttr(testSim.SIM_NAME, attr);

    ASSERT_EQ(resp.value().primitive().int_64(), 1);

    // Set the value to something else
    int newVal = 90;
    auto newValProto = bento::protos::Value();
    newValProto.mutable_primitive()->set_int_64(newVal);
    newValProto.mutable_data_type()->set_primitive(
        bento::protos::Type_Primitive_INT64);

    setAttr(testSim.SIM_NAME, attr, newValProto);

    // Ensure that the value has been updated
    resp = getAttr(testSim.SIM_NAME, attr);
    ASSERT_EQ(resp.value().primitive().int_64(), newVal);
}

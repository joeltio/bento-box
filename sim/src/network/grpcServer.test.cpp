/*
 * bentobox-sim
 * gRPC Utilities
 */

#include <iostream>
#include <gtest/gtest.h>
#include <grpc++/grpc++.h>

#include "grpc/health/v1/health.pb.h"
#include "grpc/health/v1/health.grpc.pb.h"
#include "network/grpcServer.h"
#include "service/engineService.h"

#define TEST_SUITE GRPCServer
#define TEST_PORT 50010

using grpc::ClientContext;
using grpc::CreateChannel;
using grpc::InsecureChannelCredentials;
using grpc::Service;
using grpc::Status;
using grpc::health::v1::Health;
using grpc::health::v1::HealthCheckRequest;
using grpc::health::v1::HealthCheckResponse;
using network::GRPCServer;
using std::list;
using std::string;
using std::to_string;

TEST(TEST_SUITE, StartGRPCServer) {
    // run server listening on localhost port
    // use EngineServiceImpl as a placeholder service as grpc Server
    // does not function properly with no services attached
    auto testService = EngineServiceImpl();
    list<Service *> services = {&testService};
    GRPCServer server("localhost", TEST_PORT, services);
    string expectedAddress = "localhost:" + to_string(TEST_PORT);
    ASSERT_EQ(server.port(), TEST_PORT);
    ASSERT_EQ(server.host(), "localhost");
    ASSERT_EQ(server.address(), expectedAddress);

    // check connectivity to the server by poking its health check endpoint
    HealthCheckRequest healthCheckReq;
    HealthCheckResponse healthCheckResp;
    ClientContext context;
    auto channel = CreateChannel(expectedAddress, InsecureChannelCredentials());
    auto healthClient = Health::NewStub(channel);
    Status s = healthClient->Check(&context, healthCheckReq, &healthCheckResp);
    ASSERT_TRUE(s.ok());
    ASSERT_EQ(healthCheckResp.status(), HealthCheckResponse::SERVING);
}

/*
 * bentobox-sim
 * gRPC Server
 */

#include <iostream>
#include <sstream>
#include <condition_variable>

#include "network/grpcServer.h"

using grpc::InsecureServerCredentials;
using grpc::Server;
using grpc::ServerBuilder;
using grpc::Service;
using std::condition_variable;
using std::list;
using std::lock_guard;
using std::make_pair;
using std::make_unique;
using std::move;
using std::mutex;
using std::ostringstream;
using std::pair;
using std::runtime_error;
using std::string;
using std::thread;
using std::to_string;
using std::unique_lock;
using std::unique_ptr;

namespace network {
GRPCServer::GRPCServer(const string host, const int port,
                       const list<Service *> &services) {
    // check at least one service is provided
    if (services.size() <= 0) {
        throw runtime_error(
            "At least one service must be provided when starting gRPC server");
    }
    // form address from host and port in form HOST[:PORT}
    address_ = "localhost:" + to_string(port);
    host_ = host;

    // construct grpc server with builder and register services
    grpc::EnableDefaultHealthCheckService(true);
    ServerBuilder builder;
    builder.AddListeningPort(address_, InsecureServerCredentials(), &port_);
    for (auto service : services) {
        builder.RegisterService(service);
    }
    this->server = move(builder.BuildAndStart());

    if (!this->server) {
        ostringstream errorMsg;
        errorMsg << "Could not start gRPC server";
        throw runtime_error(errorMsg.str());
    }

    // declare that the server is ready to serve on the grpc health check
    // service
    auto healthCheckSvc = this->server->GetHealthCheckService();
    healthCheckSvc->SetServingStatus(true);
}
}  // namespace network

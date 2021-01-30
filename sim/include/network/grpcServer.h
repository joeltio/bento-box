#ifndef BENTO_GRPCSERVER_H
/*
 * bentobox-sim
 * gRPC Server
 */
#include <thread>
#include <cstdint>
#include <vector>
#include <mutex>
#include <grpc++/server_builder.h>

/** Wraps gRPC Server to manage a gRPC::Server instance  */
namespace network {
class GRPCServer {
   private:
    int port_;
    std::string host_;
    std::string address_;
    // grpc::Server wrapped by this GRPCServer
    std::unique_ptr<grpc::Server> server;

   public:
    /**
     * Creates and starts a gRPC server running the services listening on the
     * given host and port. The server will accept insecure gRPC requests on the
     * given host and port.
     *
     * @param host The hostname to configure the gRPC server to listen on.
     * @param services List of gRPC services to use to serve requests received.
     *   At least  one service must be provided.
     * by the server.
     * @param port The port to configure the gRPC server to listen on. If unset,
     *   the gRPC will listen on a automatically chosen port.
     *
     * @throws runtime_error if the gRPC server fails to start.
     *
     * @returns The started gRPC server and the port number it listens on.
     */
    GRPCServer(const std::string host, const int port,
               const std::list<grpc::Service *> &services);

    /** Shutdown the wrapped gRPC::server on destruction */
    ~GRPCServer() { this->shutdown(); }

    /** Waits for this gRPC server to shutdown */
    void wait() { this->server->Wait(); }

    /** Shutdown the gRPC server, stopping it from serving requests */
    void shutdown() { this->server->Shutdown(); }
    // Getters
    /* Get the port that gRPC server listens on */
    int port() const { return port_; }
    /* Get the host that gRPC server listens on */
    std::string host() const { return host_; }
    /* Get the address that gRPC server listens on in form HOST:PORT */
    std::string address() const { return address_; }
};
}  // namespace network
#endif /* ifndef BENTO_GRPCSERVER_H */

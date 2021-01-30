/*
 * bentobox-sim
 * Main Entrypoint
 */
#include <component/textureComponent.h>
#include <core/graphicsContext.h>
#include <core/systemContext.h>
#include <core/windowContext.h>
#include <ics.h>
#include <system/render.h>
#include <network/grpcServer.h>
#include <service/engineService.h>

using grpc::Service;
using network::GRPCServer;
using service::EngineServiceImpl;
using std::invalid_argument;
using std::list;
using std::stoi;
using std::string;
using std::to_string;

/**
 * Get the value of the environment variable with the given name.
 *
 * @param name The name of environment variable to get.
 * @param defaultValue The value to return if no such environment variable is
 * found.
 *
 * @returns The value of the environment variable or defaultValue
 *  if the variable cannot be found.
 */
string getEnv(const string name, const string defaultValue) {
    auto envValue = std::getenv(name.c_str());
    if (!envValue) {
        return defaultValue;
    }
    return envValue;
}

/**
 * Bentobox-sim engine main entrypoint
 *
 * Environment Variable parameters:
 * - BENTOBOX_SIM_HOST - the host/ip that bentobox-sim listens on.
 * - BENTOBOX_SIM_PORT - the port that bentobox-sim listens on.
 */
int main(int argc, char *argv[]) {
    // setup graphics
    WindowContext windowContext = WindowContext(800, 600, "Bento Box");
    GraphicsContext graphics = GraphicsContext(windowContext);

    // setup ICS
    ics::ComponentStore componentStore = ics::ComponentStore();
    ics::index::IndexStore indexStore = ics::index::IndexStore();
    SystemContext systemContext = SystemContext<ics::index::IndexStore>();
    // register ICS components
    auto tex1 = ics::component::Texture2DComponent(1);
    auto tex2 = ics::component::Texture2DComponent(2);
    auto tex3 = ics::component::Texture2DComponent(3);
    auto tex4 = ics::component::Texture2DComponent(4);
    ics::addComponent(indexStore, componentStore, tex1);
    ics::addComponent(indexStore, componentStore, tex2);
    ics::addComponent(indexStore, componentStore, tex3);
    ics::addComponent(indexStore, componentStore, tex4);
    // register ICS systems
    const SystemFn<ics::index::IndexStore> a(&ics::system::render);
    systemContext.systems.push_front(a);

    // start gRPC server using host and port obtained via env vars
    string host = getEnv("BENTOBOX_SIM_HOST", "localhost");
    int port = std::stoi(getEnv("BENTOBOX_SIM_PORT", "54242"));

    EngineServiceImpl engineService;
    list<Service *> services = {&engineService};
    GRPCServer server(host, port, services);

    std::cout << "bentobox-sim listening on " << server.address() << std::endl;

    // run engine main loop
    while (!windowContext.shouldClose()) {
        glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);

        systemContext.run(graphics, componentStore, indexStore);

        windowContext.swapBuffers();
        windowContext.updateEvents();
    }
}

#ifndef BENTOBOX_TEST_SIMULATION_H
#define BENTOBOX_TEST_SIMULATION_H

#include <interpreter/util.h>
#include <component/userComponent.h>
#include <bento/protos/ecs.pb.h>
#include <bento/protos/sim.pb.h>

// The namespace here is crucial as a single include will mean all files have
// included this header.
namespace test_simulation {

const char TEST_COMPONENT_NAME[] = "TestComponent";

namespace {

bento::protos::ComponentDef createCompDef() {
    return interpreter::createSimpleCompDef(
        TEST_COMPONENT_NAME, {{"height", bento::protos::Type_Primitive_INT64},
                              {"width", bento::protos::Type_Primitive_INT64}});
}

}  // namespace

struct TestComponent : public ics::component::UserComponent {
    TestComponent() : UserComponent(TEST_COMPONENT_NAME, createCompDef()){};
    TestComponent(int width, int height);
};

// Creates a system that increments to attribute to 100 then resets it to 0
// The attribute must be int64
bento::protos::SystemDef cycle100System(
    const bento::protos::AttributeRef& attrRef);

struct TestSimulation {
    const char* SIM_NAME = "Test Simulation";
    const char* COMP_TYPE_NAME = TEST_COMPONENT_NAME;
    const int COMP_START_VAL = 30;

    bento::protos::EntityDef entityDef;
    const bento::protos::ComponentDef compDef = createCompDef();
    bento::protos::SimulationDef simDef;

    TestSimulation();
};

}  // namespace test_simulation

#endif  // BENTOBOX_TEST_SIMULATION_H

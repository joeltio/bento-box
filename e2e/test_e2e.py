#
# bento-box
# E2E Test
#
# Requires environment variables to be specified:
# - BENTOBOX_SIM_DOCKER - tag of the bentobox-sim docker image to run

import os
import pytest
from git import Repo
from testcontainers.core.container import DockerContainer

from bento import types
from bento.client import Client
from bento.sim import Simulation
from bento.utils import to_yaml_proto
from bento.graph.plotter import Plotter
from bento.ecs.spec import EntityDef, ComponentDef
from bento.example.specs import Velocity, Position

SIM_PORT = 54243


# define test components
Movement = ComponentDef(
    name="movement",
    schema={
        "rotation": types.float64,
        "speed": types.float64,
    },
)

Keyboard = ComponentDef(
    name="keyboard",
    schema={
        "top": types.boolean,
        "down": types.boolean,
        "left": types.boolean,
        "right": types.boolean,
    },
)


@pytest.fixture
def engine_docker():
    # since this fixture as function scope, a fresh Engine instance
    # would be created for each e2e test.
    # setup bentobox-sim container and expose engine port
    engine = DockerContainer(os.environ["BENTOBOX_SIM_DOCKER"])
    engine.with_env("BENTOBOX_SIM_PORT", SIM_PORT)
    engine.with_env("BENTOBOX_SIM_HOST", "0.0.0.0")
    engine.with_exposed_ports(SIM_PORT)
    engine.start()
    try:
        # do e2e test
        yield engine
    finally:
        # cleanup by stopping sim container at end of test
        # kill the container instead of waiting for cleanup
        engine.stop(force=True)


@pytest.fixture
def client(engine_docker):
    # setup bentobox-sdk client
    client = Client(
        host=engine_docker.get_container_host_ip(),
        port=engine_docker.get_exposed_port(SIM_PORT),
    )
    # wait for sim to start accepting connections from the SDK
    client.connect(timeout_sec=30)
    return client


@pytest.fixture
def sim(client):
    """Applies the test Simulation to the Engine"""
    controls = EntityDef(components=[Keyboard])
    car = EntityDef(components=[Movement, Velocity, Position])

    sim = Simulation(
        name="driving_sim",
        entities=[controls, car],
        components=[Keyboard, Movement, Velocity, Position],
        client=client,
    )

    @sim.system
    def control_sys(g: Plotter):
        controls = g.entity(components=[Keyboard])
        car = g.entity(components=[Movement, Velocity, Position])
        acceleration, max_speed, steer_rate = 5, 18, 10

        if controls[Keyboard].left:
            car[Movement].rotation -= steer_rate
            controls[Keyboard].left = False

        elif controls[Keyboard].right:
            car[Movement].rotation += steer_rate
            controls[Keyboard].right = False

        elif controls[Keyboard].up:
            car[Movement].speed += acceleration
            controls[Keyboard].up = False

        elif controls[Keyboard].down:
            car[Movement].speed -= acceleration
            controls[Keyboard].down = False

    @sim.system
    def physics_sys(g: Plotter):
        # compute velocity from car's rotation and speed
        car = g.entity(components=[Movement, Velocity, Position])
        heading_x, heading_y = g.cos(car[Movement].rotation), -g.sin(
            car[Movement].rotation
        )
        car[Velocity].x = car[Movement].speed * heading_x
        car[Velocity].y = car[Movement].speed * heading_y

        # update car position based on current velocity
        car[Position].x += car[Velocity].x
        car[Position].y += car[Velocity].y

    sim.start()
    return sim


def test_e2e_engine_get_version(client):
    # e2e test that we can obtain sim/engine's version via SDK
    repo = Repo(search_parent_directories=True)
    assert client.get_version() == repo.head.object.hexsha


def test_e2e_engine_apply_sim(sim):
    # check the sim's entities have populated ids
    assert len([e.id for e in sim.entities if e.id != 0]) == len(sim.entities)


def test_e2e_engine_client_list_sims(sim, client):
    # check that sim is listed
    assert client.list_sims()[0] == sim.name


def test_e2e_engine_client_get_sim(sim, client):
    # check that sim's can be retrieved by name
    applied_proto = client.get_sim(sim.name)
    assert to_yaml_proto(applied_proto) == to_yaml_proto(sim.proto)

    # test error handling when getting nonexistent sim
    has_error = False
    try:
        client.get_sim("not_found")
    except LookupError:
        has_error = True
    assert has_error


def test_e2e_engine_client_remove(sim, client):
    client.remove_sim(sim.name)
    assert len(client.list_sims()) == 0


# TODO(mrzzy): run sim

# TODO(mrzzy): get set attrs

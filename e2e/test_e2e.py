#
# bento-box
# E2E Test
#
# Requires environment variables to be specified:
# - BENTOBOX_SIM_DOCKER - tag of the bentobox-sim docker image to run

import os
import pytest
from git import Repo
from math import cos, sin
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
Meta = ComponentDef(
    name="meta",
    schema={
        "name": types.string,
        "version": types.int32,
    },
)

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
        "up": types.boolean,
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
    engine.with_env("BENTOBOX_SIM_PORT", str(SIM_PORT))
    engine.with_env("BENTOBOX_SIM_HOST", "0.0.0.0")
    engine.with_exposed_ports(SIM_PORT)
    engine.start()
    # do e2e test
    yield engine
    # print the engine's logs
    print("=" * 40, "[Engine Logs]", "=" * 40)
    print(engine._container.logs().decode())
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
    sim = Simulation(
        name="driving_sim",
        components=[Keyboard, Movement, Velocity, Position, Meta],
        entities=[
            EntityDef(components=[Keyboard]),
            EntityDef(components=[Movement, Velocity, Position, Meta]),
        ],
        client=client,
    )

    @sim.init
    def init_sim(g: Plotter):
        controls = g.entity(components=[Keyboard])
        controls[Keyboard].left = False
        controls[Keyboard].right = False
        controls[Keyboard].up = False
        controls[Keyboard].down = False

        car = g.entity(components=[Movement, Velocity, Position, Meta])
        car[Meta].name = "beetle"
        car[Meta].version = 2
        car[Movement].speed = 0.0
        car[Movement].rotation = 90.0
        car[Velocity].x = 0.0
        car[Velocity].y = 0.0
        car[Position].x = 0.0
        car[Position].y = 0.0

    @sim.system
    def control_sys(g: Plotter):
        controls = g.entity(components=[Keyboard])
        car = g.entity(components=[Movement, Velocity, Position, Meta])
        acceleration, max_speed, steer_rate = 5.0, 18.0, 10.0

        # steer car
        if controls[Keyboard].left:
            car[Movement].rotation -= steer_rate
            controls[Keyboard].left = False
        elif controls[Keyboard].right:
            car[Movement].rotation += steer_rate
            controls[Keyboard].right = False

        # accelerate/slow down car
        if controls[Keyboard].up:
            car[Movement].speed = g.min(car[Movement].speed + acceleration, max_speed)
            controls[Keyboard].up = False
        elif controls[Keyboard].down:
            car[Movement].speed = g.max(car[Movement].speed - acceleration, 0.0)
            controls[Keyboard].down = False

    @sim.system
    def physics_sys(g: Plotter):
        # compute velocity from car's rotation and speed
        car = g.entity(components=[Movement, Velocity, Position, Meta])
        # rotation
        heading_x, heading_y = g.cos(car[Movement].rotation), -g.sin(
            car[Movement].rotation
        )
        # speed
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


def test_e2e_engine_list_sims(sim, client):
    # check that sim is listed
    assert client.list_sims()[0] == sim.name


def test_e2e_engine_get_sim(sim, client):
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


def test_e2e_engine_remove(sim, client):
    # test removing simulations
    client.remove_sim(sim.name)
    assert len(client.list_sims()) == 0


def test_e2e_engine_get_set_attr(sim, client):
    # test setting/setting attributes for every primitive data type
    controls = sim.entity(components=[Keyboard])
    controls[Keyboard].left = True
    assert controls[Keyboard].left == True

    car = sim.entity(components=[Movement, Velocity, Position, Meta])
    car[Meta].name = "sedan"
    assert car[Meta].name == "sedan"
    car[Meta].version = 10
    assert car[Meta].version == 10

    car[Movement].rotation = -134.2
    assert car[Movement].rotation == -134.2
    car[Movement].speed = 23.5
    assert car[Movement].speed == 23.5


def test_e2e_engine_step_sim(sim, client):
    # TODO(mrzzy): replace this temporary workaround to trigger init graph
    # once https://github.com/joeltio/bento-box/issues/34 is fixed.
    # test init
    sim.step()

    # check that values are set correctly by init graph
    controls = sim.entity(components=[Keyboard])
    assert controls[Keyboard].left == False
    assert controls[Keyboard].right == False
    assert controls[Keyboard].up == False
    assert controls[Keyboard].left == False

    car = sim.entity(components=[Movement, Velocity, Position, Meta])
    assert car[Meta].name == "beetle"
    assert car[Meta].version == 2
    assert car[Movement].speed == 0.0
    assert car[Movement].rotation == 90.0
    assert car[Velocity].x == 0.0
    assert car[Velocity].y == 0.0
    assert car[Position].x == 0.0
    assert car[Position].y == 0.0

    controls[Keyboard].up = True
    controls[Keyboard].left = True

    # test running simulation for one step
    sim.step()

    # test attributes have been updated by system
    assert controls[Keyboard].left == False
    assert controls[Keyboard].up == False
    assert car[Movement].speed == 5
    assert car[Movement].rotation == 80

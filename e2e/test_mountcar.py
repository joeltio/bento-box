#
# bento-box
# E2E Test for Mountain Car Simulation
#

from bento.utils import to_yaml_proto
import pytest

from math import cos, isclose
from bento.graph.plotter import Plotter
from bento.example.specs import Velocity, Position
from bento.example.mountcar import MountainCar, Action, State
from bento.sim import Simulation

FLOAT_TOLERANCE = 1e-1


@pytest.fixture
def sim(client):
    sim = Simulation.from_def(MountainCar, client)
    sim.start()
    return sim


def test_e2e_mountcar_init(sim):
    # check that the init graph has initalized attribute values correctly
    car = sim.entity(components=[Velocity, Position])
    assert car[Velocity].x == 0.0
    assert -0.6 <= car[Position].x <= -0.4

    env = sim.entity(components=[Action, State])
    assert env[State].reward == 0
    assert env[State].ended == False
    assert env[Action].accelerate == 1


def test_e2e_mountcar_action_accelerate(sim):
    env = sim.entity(components=[Action, State])
    car = sim.entity(components=[Velocity, Position])

    acceleration, gravity, max_speed = 0.001, 0.0025, 0.07
    car[Position].x = -0.6

    # accelerate left
    env[Action].accelerate = 0
    expected_pos_x = car[Position].x
    sim.step()
    expected_velocity_x = -acceleration
    expected_velocity_x += cos(3 * expected_pos_x) * (-gravity)
    expected_pos_x += expected_velocity_x
    assert isclose(car[Velocity].x, expected_velocity_x, rel_tol=FLOAT_TOLERANCE)
    assert isclose(car[Position].x, expected_pos_x, rel_tol=FLOAT_TOLERANCE)

    # accelerate right
    env[Action].accelerate = 2
    expected_pos_x = car[Position].x
    sim.step()
    expected_velocity_x += acceleration
    expected_velocity_x += cos(3 * expected_pos_x) * (-gravity)
    expected_pos_x += expected_velocity_x
    assert isclose(car[Velocity].x, expected_velocity_x, rel_tol=FLOAT_TOLERANCE)
    assert isclose(car[Position].x, expected_pos_x, rel_tol=FLOAT_TOLERANCE)

    # no acceleration
    env[Action].accelerate = 1
    expected_pos_x = car[Position].x
    sim.step()
    expected_velocity_x += cos(3 * expected_pos_x) * (-gravity)
    expected_pos_x += expected_velocity_x
    assert isclose(car[Velocity].x, expected_velocity_x, rel_tol=FLOAT_TOLERANCE)
    assert isclose(car[Position].x, expected_pos_x, rel_tol=FLOAT_TOLERANCE)


def test_e2e_mountcar_collision(sim):
    car = sim.entity(components=[Velocity, Position])
    # setup velocity & position such that collision occurs at -1.2
    car[Velocity].x = -0.01
    car[Position].x = -1.2
    sim.step()
    assert car[Velocity].x == 0.0
    assert car[Position].x == -1.2


def test_e2e_mountcar_reward_end_condition(sim):
    env = sim.entity(components=[Action, State])
    car = sim.entity(components=[Velocity, Position])

    # has not reached target flagpole
    pos_x = 0.0
    car[Position].x = 0.0
    sim.step()
    assert env[State].reward == -1
    assert env[State].ended == False

    # past the target flagpole
    car[Position].x = 0.6
    sim.step()
    assert env[State].reward == 0
    assert env[State].ended == True

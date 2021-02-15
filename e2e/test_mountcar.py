#
# bento-box
# E2E Test for Mountain Car Simulation
#

from bento.utils import to_yaml_proto
import pytest

from math import cos
from bento.graph.plotter import Plotter
from bento.example.specs import Velocity, Position
from bento.example.mountcar import MountainCar, Action, State
from bento.sim import Simulation


@pytest.fixture
def sim(client):
    sim = Simulation.from_def(MountainCar, client)
    sim.start()
    return sim

def test_e2e_mountcar_init(sim):
    # check that the init graph has initalized attribute values correctlya
    car = sim.entity(components=[Velocity, Position])
    car[Velocity].x = 0.0
    car[Position].x = 0.0

    env = sim.entity(components=[Action, State])
    env[State].reward = 0
    env[State].ended = False

def test_e2e_mountcar_action_accelerate(sim):
    env = sim.entity(components=[Action, State])
    car = sim.entity(components=[Velocity, Position])

    acceleration, gravity, max_speed = 0.001, 0.0025, 0.07

    # accelerate left
    env[Action].accelerate = 0
    sim.step()
    expected_velocity_x = -acceleration
    expected_velocity_x += cos(3 * expected_velocity_x) * (-gravity)
    expected_pos_x = expected_velocity_x
    assert car[Velocity].x == expected_velocity_x
    assert car[Position].x == expected_pos_x

    # accelerate right
    env[Action].accelerate = 2
    sim.step()
    expected_velocity_x += acceleration
    expected_velocity_x += cos(3 * expected_velocity_x) * (-gravity)
    expected_pos_x += expected_velocity_x
    assert car[Velocity].x == expected_velocity_x
    assert car[Position].x == expected_pos_x

    # no acceleration
    env[Action].accelerate = 1
    sim.step()
    expected_velocity_x += cos(3 * expected_velocity_x) * (-gravity)
    expected_pos_x += expected_velocity_x
    assert car[Velocity].x == expected_velocity_x
    assert car[Position].x == expected_pos_x


def test_e2e_mountcar_collision(sim):
    car = sim.entity(components=[Velocity, Position])
    # setup velocity & position such that collision occurs at -1.2
    car[Velocity].x = -0.01
    car[Position].x = -1.2
    sim.step()
    assert car[Velocity].x == 0.0
    assert car[Position].x == -1.2


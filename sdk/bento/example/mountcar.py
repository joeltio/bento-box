#
# bentobox-sdk
# mountain car example simulation
#

from bento import types
from bento.graph.plotter import Plotter
from bento.spec.ecs import ComponentDef, EntityDef

from bento.example.specs import Velocity, Position
from bento.sim import Simulation
from bento.spec.sim import SimulationDef

Action = ComponentDef(
    name="action",
    schema={
        "accelerate": types.int32,
    },
)
"""
Action allows the agent to control the car in the Simulation via its acceleration.

Attributes:
    **accelerate** (`types.int32`): Set the acceleration of the car.

    - 0: Accelerate to the Left
    - 1: Don't accelerate
    - 2: Accelerate to the Right
"""

State = ComponentDef(
    name="state",
    schema={
        "reward": types.int32,
        "ended": types.boolean,
    },
)
"""
State tracks the current state of the Simulation.

Attributes:
    **reward** (`types.int32`): Reward given to agent for the current Simulation step:

    - Reward of 0 is awarded if the agent reached the flag (`Position.x >= 0.5`) on top of the mountain.
    - Reward of -1 is penalized if the position of the agent `Position.x < 0.5`

    **ended** (`types.boolean`): Whether the Simulation is has ended (`Position.x > 0.5`).
"""

MountainCar = SimulationDef(
    name="mountain_car",
    components=[Velocity, Position, Action, State],
    entities=[
        EntityDef(components=[Velocity, Position]),
        EntityDef(components=[Action, State]),
    ],
)
"""
Mountain Car Simulation implemented using `bento`

A car is started at random position the bottom of a valley.
The agent may choose to accelerate the car to the left, right or cease any acceleration.
The objective of the Simulation is to reach the flag on top of the mountain at `Position.x > 0.5`
The simulation ends when the car's `Position.x > 0.5`
"""


@MountainCar.init
def init_fn(g: Plotter):
    car = g.entity(components=[Velocity, Position])
    car[Velocity].x = 0.0
    car[Position].x = g.random(-0.6, -0.4)

    env = g.entity(components=[Action, State])
    env[State].reward = 0
    env[State].ended = False
    env[Action].accelerate = 1


@MountainCar.system
def sim_fn(g: Plotter):
    env = g.entity(components=[Action, State])
    car = g.entity(components=[Velocity, Position])

    # process car physics
    # compute velocity based on acceleration action & decceleration due to gravity
    acceleration, gravity, max_speed = 0.001, 0.0025, 0.07
    # apply acceleration based on accelerate action:
    # 0: Accelerate to the Left
    # 1: Don't accelerate
    # 2: Accelerate to the Right
    car[Velocity].x += (env[Action].accelerate - 1) * acceleration
    # apply gravity inverse to the mountain path used by the car
    # the mountain is defined by y = sin(3*x)
    # as such we apply gravity inversely using y = cos(3*x)
    # apply negative gravity as gravity works in the opposite direction of movement
    car[Velocity].x += g.cos(3 * car[Position].x) * (-gravity)
    car[Velocity].x = g.clip(car[Velocity].x, min_x=-max_speed, max_x=max_speed)

    # compute new position from current velocity
    min_position, max_position = -1.2, 0.6
    car[Position].x += car[Velocity].x
    car[Position].x = g.clip(car[Position].x, min_position, max_position)

    # collision: stop car when colliding with min_position
    if car[Position].x <= min_position:
        car[Velocity].x = 0.0

    # resolve simulation state: reward and simulation completition
    env[State].reward = 0 if car[Position].x >= 0.5 else -1
    env[State].ended = True if car[Position].x > 0.5 else False

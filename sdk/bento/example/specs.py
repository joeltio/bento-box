#
# Bentobox
# SDK
# Example Specs
#
"""
Example ECS Component types implemented using `bento.spec.ecs.ComponentDef`
"""


from bento.spec.ecs import ComponentDef
from bento import types

Position = ComponentDef(
    name="position",
    schema={
        "x": types.float64,
        "y": types.float64,
    },
)
"""
Records the current position of an Entity

Attributes:
    **x** (`float64`): The position of the Entity on the x axis.

    **y** (`float64`): The position of the Entity on the y axis.
"""


Velocity = ComponentDef(
    name="velocity",
    schema={
        "x": types.float64,
        "y": types.float64,
    },
)
"""
The current velocity an Entity is moving at.

Attributes:
    **x** (`float64`): The velocity of the Entity on the x axis.

    **y** (`float64`): The velocity of the Entity on the y axis.
"""


Speed = ComponentDef(
    name="speed",
    schema={
        "max_x": types.float64,
        "max_y": types.float64,
    },
)

Clock = ComponentDef(
    name="clock",
    schema={
        "tick_ms": types.int64,
    },
)

Keyboard = ComponentDef(
    name="keyboard",
    schema={
        "pressed": types.string,
    },
)

#
# Bentobox
# SDK
# Example Specs
#


from bento.ecs.spec import ComponentDef
from bento import types

Position = ComponentDef(
    name="position",
    schema={
        "x": types.float64,
        "y": types.float64,
    },
)

Velocity = ComponentDef(
    name="velocity",
    schema={
        "x": types.float64,
        "y": types.float64,
    },
)

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

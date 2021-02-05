#
# Bentobox
# SDK - Graph Tests
# Test Specs
#


from bento.ecs.spec import ComponentDef
from bento import types

Position = ComponentDef(
    name="position",
    schema={
        "x": types.int32,
        "y": types.int32,
    },
)

Velocity = ComponentDef(
    name="velocity",
    schema={
        "x": types.int32,
        "y": types.int32,
    },
)

Speed = ComponentDef(
    name="speed",
    schema={
        "max_x": types.int32,
        "max_y": types.int32,
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

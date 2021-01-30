#
# Bentobox
# SDK - Graph Tests
# Test components
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

Speed = ComponentDef(
    name="speed",
    schema={
        "x_neg": types.int32,
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

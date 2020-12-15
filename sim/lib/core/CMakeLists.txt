# glad library
add_library(glad
    lib/glad/src/glad.c
)
target_include_directories(glad
    PUBLIC lib/glad/include
)

# glfw library
find_package(glfw3 3 REQUIRED)

# core library
add_library(core
    include/core/graphicsContext.h
    src/graphicsContext.cpp
    include/core/systemContext.h
    src/systemContext.cpp
    include/core/windowContext.h
    src/windowContext.cpp
)
target_include_directories(core
    PRIVATE lib/stb_image
    PUBLIC include
)
target_link_libraries(core
    PUBLIC glfw
    PUBLIC glad
)
if (NOT WIN32)
    target_link_libraries(core
        PRIVATE dl
    )
endif()

# core test
add_executable(core-test
    src/ics/component.test.cpp
    src/ics/componentManager.test.cpp
    src/ics/compVec.test.cpp
    src/ics/util/composable.test.cpp
    src/ics/util/typeMap.test.cpp
)
target_link_libraries(core-test
    PRIVATE core
    PRIVATE gtest_main
)

# Export libraries with namespaced name
add_library(bento::core ALIAS core)

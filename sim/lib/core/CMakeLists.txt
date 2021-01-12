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
    src/graphicsContext.cpp
    src/windowContext.cpp
    src/ics/componentStore.cpp
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
add_library(core-test
    src/systemContext.test.cpp
    src/ics/component.test.cpp
    src/ics/componentStore.test.cpp
    src/ics/compVec.test.cpp
    src/ics/util/composable.test.cpp
    src/ics/util/setIntersection.test.cpp
    src/ics/util/typeMap.test.cpp
)
target_link_libraries(core-test
    PRIVATE core
    PRIVATE gtest
)

# Export libraries with namespaced name
add_library(bento::core ALIAS core)
add_library(bento::core-test ALIAS core-test)

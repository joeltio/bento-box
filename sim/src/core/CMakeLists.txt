SET(LIB_NAME core)
SET(LIB_TEST_NAME "${LIB_NAME}-test")
SET(SOURCES graphicsContext.h graphicsContext.cpp windowContext.h windowContext.cpp)
SET(TESTS)

add_library(
    ${LIB_NAME}
    ${SOURCES}
)

add_library(
    ${LIB_TEST_NAME}
    ${SOURCES}
    ${TESTS}
)

SET(TARGETS ${LIB_NAME} ${LIB_TEST_NAME})

# Cmake could not determine the language used from the files
# https://stackoverflow.com/questions/11801186/cmake-unable-to-determine-linker-language-with-c
foreach(target ${TARGETS})
    set_target_properties(${target} PROPERTIES LINKER_LANGUAGE CXX)
    target_include_directories(${target} PRIVATE ".")
endforeach()

## Library Dependencies
# ICS library
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/ics")
target_link_libraries(${LIB_NAME} PUBLIC ics)
target_link_libraries("${LIB_TEST_NAME}" PUBLIC -Wl,--whole-archive,--as-needed ics-test -Wl,--no-whole-archive,--as-needed)

# GLFW
find_package(glfw3 3 REQUIRED)
foreach(target ${TARGETS})
    target_link_libraries(${target} PUBLIC glfw)
endforeach()

# GLAD
set(GLAD_DIR "${CMAKE_SOURCE_DIR}/lib/glad")
add_library(glad "${GLAD_DIR}/src/glad.c")
target_include_directories(glad PRIVATE "${GLAD_DIR}/include")

foreach(target ${TARGETS})
    target_include_directories(${target} PUBLIC "${GLAD_DIR}/include")
    target_link_libraries(${target} PUBLIC glad)
    # On non-windows systems, GLAD requires libdl to be linked
    if(NOT WIN32)
        target_link_libraries(${target} PUBLIC dl)
    endif(NOT WIN32)
endforeach()

# Google test
target_link_libraries(${LIB_TEST_NAME} PRIVATE gtest)

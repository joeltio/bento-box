cmake_minimum_required(VERSION 3.16)
project(bentobox)

# Source files
set(SRC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src")
set(LIB_DIR "${CMAKE_CURRENT_SOURCE_DIR}/lib")
set(ICS_DIR "${SRC_DIR}/ics")
set(UTIL_DIR "${SRC_DIR}/util")

set(SOURCES
    "${SRC_DIR}/main.cpp"
)
set(TESTS
    "${SRC_DIR}/test.cpp"
    "${UTIL_DIR}/typeMap.test.cpp"
    "${ICS_DIR}/component.test.cpp"
)

# Executable
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_executable(${PROJECT_NAME} ${SOURCES})
add_executable("${PROJECT_NAME}_test" ${TESTS})
target_include_directories(${PROJECT_NAME} PRIVATE ${SRC_DIR})

## Dependencies
# GLFW
find_package(glfw3 3 REQUIRED)
target_link_libraries(${PROJECT_NAME} PRIVATE glfw)

# GLAD
set(GLAD_DIR "${LIB_DIR}/glad")
add_library(glad "${GLAD_DIR}/src/glad.c")
target_include_directories(glad PRIVATE "${GLAD_DIR}/include")
target_include_directories(${PROJECT_NAME} PRIVATE "${GLAD_DIR}/include")
target_link_libraries(${PROJECT_NAME} PRIVATE glad)
target_include_directories("${PROJECT_NAME}_test" PRIVATE "${GLAD_DIR}/include")
target_link_libraries("${PROJECT_NAME}_test" PRIVATE glad)

# On non-windows systems, GLAD requires libdl to be linked
if(NOT WIN32)
target_link_libraries(${PROJECT_NAME} PRIVATE dl)
target_link_libraries("${PROJECT_NAME}_test" PRIVATE dl)
endif(NOT WIN32)

## Test Dependencies
# Google test
add_subdirectory(
    "${LIB_DIR}/googletest/googletest"
    "${LIB_DIR}/googletest/googlemock"
    EXCLUDE_FROM_ALL)
target_link_libraries("${PROJECT_NAME}_test" PRIVATE gtest_main)

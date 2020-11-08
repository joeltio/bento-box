cmake_minimum_required(VERSION 3.16)
# use new policy for options
set(CMAKE_POLICY_DEFAULT_CMP0077 NEW)
project(bentobox)

# Source files
set(SRC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src")
set(ICS_DIR "${SRC_DIR}/ics")
set(UTIL_DIR "${SRC_DIR}/util")
set(LIB_DIR "${CMAKE_CURRENT_SOURCE_DIR}/lib")
set(PROTOS_DIR "${CMAKE_CURRENT_BINARY_DIR}/protos")

file(GLOB PROTO_SOURCES "${PROTOS_DIR}/protos/*.pb.cc")
set(SOURCES
    "${SRC_DIR}/main.cpp"
    ${PROTO_SOURCES}
)
set(TESTS
    "${SRC_DIR}/main.test.cpp"
    ${PROTO_SOURCES}
)

# Executable
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_executable(${PROJECT_NAME} ${SOURCES})
target_include_directories(${PROJECT_NAME} PRIVATE ${SRC_DIR} ${PROTOS_DIR})
add_executable("${PROJECT_NAME}_test" ${TESTS})
target_include_directories("${PROJECT_NAME}_test" PRIVATE ${SRC_DIR} ${PROTOS_DIR})

# Link subdir modules
foreach (lib IN ITEMS util ics)
    add_subdirectory("${SRC_DIR}/${lib}")
    target_link_libraries(${PROJECT_NAME} PRIVATE ${lib})
    target_link_libraries("${PROJECT_NAME}_test" PRIVATE -Wl,--whole-archive ${lib}-test -Wl,--no-whole-archive)
endforeach()

## Library Dependencies
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

# Protobuf
set(PROTOBUF_DIR "{LIB_DIR}/protobuf")
# disable redudant building of unused dependencies
set(protobuf_BUILD_TESTS FALSE)
set(protobuf_BUILD_EXAMPLES FALSE)
set(protobuf_BUILD_CONFORMANCE FALSE)
set(protobuf_BUILD_LIBPROTOC FALSE)
set(protobuf_BUILD_PROTOC_BINARIES FALSE)
set(protobuf_BUILD_SHARED_LIBS FALSE)
add_subdirectory(
    "${LIB_DIR}/protobuf/cmake"
    EXCLUDE_FROM_ALL
)
target_include_directories(${PROJECT_NAME} PRIVATE "${PROTOBUF_DIR}/src")
target_link_libraries(${PROJECT_NAME} PRIVATE libprotobuf)
target_include_directories("${PROJECT_NAME}_test" PRIVATE "${PROTOBUF_DIR}/src")
target_link_libraries("${PROJECT_NAME}_test" PRIVATE libprotobuf)

# On non-windows systems, GLAD requires libdl to be linked
if(NOT WIN32)
target_link_libraries(${PROJECT_NAME} PRIVATE dl)
target_link_libraries("${PROJECT_NAME}_test" PRIVATE dl)
endif(NOT WIN32)

## Test Dependencies
# Google test
add_subdirectory(
    "${LIB_DIR}/googletest"
    EXCLUDE_FROM_ALL
)
target_link_libraries("${PROJECT_NAME}_test" PRIVATE gtest_main)

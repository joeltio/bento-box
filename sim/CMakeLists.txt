cmake_minimum_required(VERSION 3.16)
# use cmake policy to make option() to honor normal variables
# http://shadow.nd.rl.ac.uk/ICP_Binaries/CMake/doc/cmake/html/policy/CMP0077.html
set(CMAKE_POLICY_DEFAULT_CMP0077 NEW)
project(bentobox)

# allow cmake modules under cmake/ to be imported
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

## Executable
# release: use optimzations
set(CMAKE_CXX_FLAGS_RELEASE "-O2")
# debug: include debugging info, show colors and enable warnings
set(CMAKE_CXX_FLAGS_DEBUG "-g")
# target bento simulator's executables to c++ 20
set(CMAKE_CXX_STANDARD 20)
# pull git commit hash from git and make it avaiable via a templated file
include(GetGitRevisionDescription)
set(GENERATED_INCLUDES "${CMAKE_CURRENT_BINARY_DIR}/include")
file(MAKE_DIRECTORY ${GENERATED_INCLUDES})
get_git_head_revision(GIT_REF GIT_HASH ALLOW_LOOKING_ABOVE_CMAKE_SOURCE_DIR)
configure_file("include/git.h.in" "${GENERATED_INCLUDES}/git.h" @ONLY)

# define source files/tests as any .cpp or .test.cpp under src/ respectively
# (excluding main.cpp/main.test.cpp for each target)
file(GLOB_RECURSE SOURCES  "src/*.cpp") 
list(FILTER SOURCES EXCLUDE REGEX "(\.test\.cpp$|.*main\..*)")
file(GLOB_RECURSE TEST_SOURCES "src/*.test.cpp")
list(FILTER TEST_SOURCES EXCLUDE REGEX ".*main\..*")

# define build targets
set(TARGET_SIM ${PROJECT_NAME})
set(TARGET_TEST "${PROJECT_NAME}-test")
set(TARGETS ${TARGET_SIM} ${TARGET_TEST})

add_executable(${TARGET_SIM}
    ${SOURCES}
    src/main.cpp
)
target_include_directories(${TARGET_SIM}
    PUBLIC include
    ${GENERATED_INCLUDES}
)

add_executable(${TARGET_TEST}
    ${SOURCES}
    ${TEST_SOURCES}
    src/main.test.cpp
)
target_include_directories(${TARGET_TEST}
    PUBLIC include
    ${GENERATED_INCLUDES}
)

add_subdirectory("lib/core")
target_link_libraries(${TARGET_SIM}
    PRIVATE bento::core
)
target_link_libraries(${TARGET_TEST}
    PRIVATE bento::core
    # When --whole-archive is needed to ensure that core-test's tests are not lost when
    # they are linked to the test target. The core-test's tests are lost because they
    # are not referenced. This flag ensures that the tests are retained.
    PRIVATE -Wl,--whole-archive bento::core-test -Wl,--no-whole-archive
)

## Library Dependencies
# fetch dependencies
include(dependencies)

# GRPC/Protobuf
# link protobuf/grpc libraries
foreach(target IN ITEMS ${TARGETS})
    target_include_directories(${target} PRIVATE "${PROTOBUF_DIR}/src")
    target_link_libraries(${target} PRIVATE libprotobuf grpc++ grpc++_reflection)
endforeach()

# Compile and link protobuf c++ bindings from protobuf definitions
get_filename_component(PROTOS_DIR "../protos" ABSOLUTE)
# target directory to write protobuf bindings to
set(PROTO_BINDS_DIR "${CMAKE_CURRENT_BINARY_DIR}/protos")
file(MAKE_DIRECTORY ${PROTO_BINDS_DIR})
# list protobuf definitions in protos/
file(GLOB BENTO_PROTO_DEFS "${PROTOS_DIR}/bento/protos/*.proto")
file(GLOB GRPC_HEALTH_PROTO_DEFS "${PROTOS_DIR}/grpc/health/v1/*.proto")
set(PROTO_DEFS ${BENTO_PROTO_DEFS} ${GRPC_HEALTH_PROTO_DEFS})

# replace .proto with .pb.cc and .pb.h
string(REPLACE "${PROTOS_DIR}" "${PROTO_BINDS_DIR}" PROTO_BINDS "${PROTO_DEFS}")
string(REPLACE ".proto" ".pb.cc" PROTO_BIND_SOURCES "${PROTO_BINDS}")
string(REPLACE ".proto" ".grpc.pb.cc" PROTO_GRPC_SOURCES "${PROTO_BINDS}")
string(REPLACE ".proto" ".pb.h" PROTO_BIND_HEADERS "${PROTO_BINDS}")
# run protoc with grpc_cpp_plugin to generate c++ bindings
add_custom_command(
    OUTPUT ${PROTO_BIND_HEADERS} ${PROTO_BIND_SOURCES} ${PROTO_GRPC_SOURCES}
    COMMAND $<TARGET_FILE:protoc>
    ARGS
        -I ${PROTOS_DIR}
        --grpc_out ${PROTO_BINDS_DIR}
        --cpp_out ${PROTO_BINDS_DIR}
        --plugin=protoc-gen-grpc=$<TARGET_FILE:grpc_cpp_plugin>
        ${PROTO_DEFS}
    DEPENDS ${PROTO_DEFS} $<TARGET_FILE:protoc> $<TARGET_FILE:grpc_cpp_plugin>
)
foreach(target IN ITEMS ${TARGETS})
    target_sources(${target} PRIVATE ${PROTO_BIND_SOURCES} ${PROTO_GRPC_SOURCES})
    target_include_directories(${target} PRIVATE ${PROTO_BINDS_DIR})
endforeach()

## Test Dependencies
# link googletest
target_link_libraries(${TARGET_TEST} PRIVATE -Wl,--no-whole-archive gtest_main)

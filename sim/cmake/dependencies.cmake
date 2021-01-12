#
# bentobox-sim
# Library Dependencies
#

cmake_minimum_required(VERSION 3.16)
include(FetchContent)

# show progress for when fetching FetchContent dependencies
set(FETCHCONTENT_QUIET OFF)
# target library dependencies to c++ 17
set(CMAKE_CXX_STANDARD 17)

# GRPC/Protobuf
# disable unused protobuf targets
set(protobuf_BUILD_TESTS OFF)
# disable unused grpc plugin targets
set(gRPC_BUILD_CSHARP_EXT OFF)
set(gRPC_BUILD_GRPC_CSHARP_PLUGIN OFF)
set(gRPC_BUILD_GRPC_NODE_PLUGIN OFF)
set(gRPC_BUILD_GRPC_OBJECTIVE_C_PLUGIN OFF)
set(gRPC_BUILD_GRPC_PHP_PLUGIN OFF)
set(gRPC_BUILD_GRPC_PYTHON_PLUGIN OFF)
set(gRPC_BUILD_GRPC_RUBY_PLUGIN OFF)
# disable abseil tests targets
set(BUILD_TESTING OFF)
FetchContent_Declare(
    grpc
    GIT_REPOSITORY https://github.com/grpc/grpc.git
    GIT_TAG        v1.33.2
    GIT_PROGRESS   TRUE
)
FetchContent_MakeAvailable(grpc)

# Google test
FetchContent_Declare(
  googletest
  GIT_REPOSITORY https://github.com/google/googletest.git
  GIT_TAG        release-1.10.0
  GIT_PROGRESS   TRUE
)
FetchContent_MakeAvailable(googletest)

# phony/target that does pulls & builds in dependencies
set(TARGET_DEPS "deps")
add_custom_target(
    ${TARGET_DEPS}
    DEPENDS libprotobuf grpc++ grpc++_reflection gtest_main
)

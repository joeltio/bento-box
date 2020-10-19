cmake_minimum_required(VERSION 3.17)
project(learngl)

set(CMAKE_CXX_STANDARD 20)

add_executable(learngl src/main.cpp)


add_library(glad lib/glad.c)
find_package(glfw3 3.3 REQUIRED)
target_link_libraries(learngl PRIVATE glad)
target_link_libraries(learngl PRIVATE glfw)

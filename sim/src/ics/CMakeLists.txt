SET(LIB_NAME ics)
SET(SOURCES component.h compVec.h index.h)
SET(TESTS component.test.cpp compVec.test.cpp index.test.cpp)

add_library(
    ${LIB_NAME}
    ${SOURCES}
)

add_library(
    ${LIB_NAME}-test
    ${SOURCES}
    ${TESTS}
)

# Cmake could not determine the language used from the files
# https://stackoverflow.com/questions/11801186/cmake-unable-to-determine-linker-language-with-c
set_target_properties(${LIB_NAME} PROPERTIES LINKER_LANGUAGE CXX)
set_target_properties(${LIB_NAME}-test PROPERTIES LINKER_LANGUAGE CXX)

target_include_directories(${LIB_NAME} PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}")
target_include_directories(${LIB_NAME}-test PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}")

# Google test
target_link_libraries("${LIB_NAME}-test" PRIVATE gtest)

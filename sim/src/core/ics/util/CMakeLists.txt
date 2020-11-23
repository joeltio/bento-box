SET(LIB_NAME util)
SET(SOURCES typeMap.h)
SET(TESTS typeMap.test.cpp)

add_library(
    ${LIB_NAME}
    ${SOURCES}
)

add_library(
    "${LIB_NAME}-test"
    ${SOURCES}
    ${TESTS}
)

# Cmake could not determine the language used from the files
# https://stackoverflow.com/questions/11801186/cmake-unable-to-determine-linker-language-with-c
set_target_properties(${LIB_NAME} PROPERTIES LINKER_LANGUAGE CXX)
set_target_properties("${LIB_NAME}-test" PROPERTIES LINKER_LANGUAGE CXX)

target_include_directories(${LIB_NAME} PRIVATE ".")
target_include_directories("${LIB_NAME}-test" PUBLIC ".")

# Google test
target_link_libraries("${LIB_NAME}-test" PRIVATE gtest)

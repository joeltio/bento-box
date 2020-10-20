#
# bento-box
# project makefile
#

.PHONY: build

BUILD_DIR:=build
SRC_DIR:=bento-box/
CMAKE:=cmake

build:
	$(CMAKE) -S $(SRC_DIR) -B $(BUILD_DIR)
	$(CMAKE) --build $(BUILD_DIR)

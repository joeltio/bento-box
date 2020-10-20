#
# bento-box
# project makefile
#

.PHONY: build test clean run

TARGET:=bentobox
TEST_TARGET:=bentobox_test
BUILD_DIR:=build
SRC_DIR:=bento-box/

CMAKE:=cmake
RM:=rm -rf

build:
	$(CMAKE) -S $(SRC_DIR) -B $(BUILD_DIR)
	$(CMAKE) --build $(BUILD_DIR)

test: build
	$(BUILD_DIR)/$(TEST_TARGET)

run: build
	$(BUILD_DIR)/$(TARGET)

clean:
	$(RM) $(BUILD_DIR)

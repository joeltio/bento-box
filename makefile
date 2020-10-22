#
# bento-box
# project makefile
#

# command aliases
CMAKE:=cmake
RM:=rm -rf

.PHONY: build test clean run

build: build-sim

test: test-sim

clean: clean-sim

## Bento Box: Simulator component 
SIM_TARGET:=bentobox
SIM_TEST:=bentobox_test
SIM_SRC:=sim
SIM_BUILD_DIR:=sim/build

.PHONY: build-sim test-sim clean-sim
build-sim:
	$(CMAKE) -S $(SIM_SRC) -B $(SIM_BUILD_DIR)
	$(CMAKE) --build $(SIM_BUILD_DIR)

test-sim: build-sim
	$(SIM_BUILD_DIR)/$(SIM_TEST)

run-sim: build-sim
	$(SIM_BUILD_DIR)/$(SIM_TARGET)

clean-sim:
	$(RM) $(SIM_BUILD_DIR)

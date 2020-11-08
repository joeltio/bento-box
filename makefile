#
# bento-box
# project makefile
#

# command aliases
CMAKE:=cmake
RM:=rm -rf
PROTOC:=protoc
MKDIR:=mkdir -p

.PHONY: build test clean run

build: build-sim

test: test-sim

clean: clean-sim

## Protobuf/GRPC API
PROTOS_DIR:=protos
PROTOS:=$(wildcard protos/*.proto)

## Bento Box: Simulator component 
SIM_TARGET:=bentobox
SIM_TEST:=bentobox_test
SIM_SRC:=sim
SIM_BUILD_DIR:=sim/build
SIM_PROTOS_DIR:=$(SIM_BUILD_DIR)/protos/protos

.PHONY: build-sim test-sim clean-sim build-protos-sim

$(SIM_PROTOS_DIR): $(PROTOS_DIR)
	$(MKDIR) $(SIM_PROTOS_DIR)
	$(PROTOC) -I=$(PROTOS_DIR) --cpp_out=$(SIM_PROTOS_DIR) $(PROTOS)

build-sim:  $(SIM_PROTOS_DIR)
	$(CMAKE) -S $(SIM_SRC) -B $(SIM_BUILD_DIR)
	$(CMAKE) --build $(SIM_BUILD_DIR) --parallel $(shell nproc --all)

test-sim: build-sim
	$(SIM_BUILD_DIR)/$(SIM_TEST)

run-sim: build-sim
	$(SIM_BUILD_DIR)/$(SIM_TARGET)

clean-sim:
	$(RM) $(SIM_BUILD_DIR)

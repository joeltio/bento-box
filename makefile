#
# bento-box
# project makefile
#

# command aliases
CMAKE:=cmake
RM:=rm -rf
PROTOC:=protoc
MKDIR:=mkdir -p
MV:=mv -f

.PHONY: deps build test clean run

build: build-sim

test: test-sim

clean: clean-sim
	
# deps: convience rules for installing dependencies
ARCH:=$(shell uname -i)
deps: dep-protoc

PROTOC_VERSION:=3.13.0

dep-protoc:
	curl -LO https://github.com/protocolbuffers/protobuf/releases/download/v$(PROTOC_VERSION)/protoc-$(PROTOC_VERSION)-linux-$(ARCH).zip 
	unzip -d /tmp/protoc protoc-$(PROTOC_VERSION)-linux-$(ARCH).zip 
	$(MV) /tmp/protoc/bin/* /usr/local/bin 
	$(RM) protoc-$(PROTOC_VERSION)-linux-$(ARCH).zip && $(RM) /tmp/protoc

## Protobuf/GRPC API
PROTOS_DIR:=protos
PROTOS:=$(wildcard protos/*.proto)

## Bento Box: Simulator component 
SIM_TARGET:=bentobox
SIM_TEST:=bentobox_test
SIM_SRC:=sim
SIM_BUILD_DIR:=sim/build

.PHONY: build-sim test-sim clean-sim

build-sim:
	$(CMAKE) -S $(SIM_SRC) -B $(SIM_BUILD_DIR)
	$(CMAKE) --build $(SIM_BUILD_DIR) --parallel $(shell nproc --all)

test-sim: build-sim
	$(SIM_BUILD_DIR)/$(SIM_TEST)

run-sim: build-sim
	$(SIM_BUILD_DIR)/$(SIM_TARGET)

clean-sim:
	$(RM) $(SIM_BUILD_DIR)

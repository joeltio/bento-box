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
	
# deps: convenience rules for installing dependencies
ARCH:=$(shell uname -i)
BIN_DIR:=/usr/local/bin
deps: dep-protoc

PROTOC_VERSION:=3.13.0

dep-protoc: /usr/local/bin/protoc

/usr/local/bin/protoc:
	curl -LO https://github.com/protocolbuffers/protobuf/releases/download/v$(PROTOC_VERSION)/protoc-$(PROTOC_VERSION)-linux-$(ARCH).zip 
	unzip -d /tmp/protoc protoc-$(PROTOC_VERSION)-linux-$(ARCH).zip 
	$(MV) /tmp/protoc/bin/* ${BIN_DIR}
	$(RM) protoc-$(PROTOC_VERSION)-linux-$(ARCH).zip && $(RM) /tmp/protoc

## Protobuf/GRPC API
PROTOS_DIR:=protos
PROTOS:=$(wildcard protos/*.proto)

## Bento - Simulator component 
SIM_TARGET:=bentobox
SIM_TEST:=bentobox_test
SIM_SRC:=sim
SIM_BUILD_DIR:=sim/build

.PHONY: build-sim test-sim clean-sim

build-sim:
	$(CMAKE) -S $(SIM_SRC) -B $(SIM_BUILD_DIR) -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
	$(CMAKE) --build $(SIM_BUILD_DIR) --parallel $(shell nproc --all) \
		--target $(SIM_TARGET) --target $(SIM_TEST)

test-sim: build-sim
	$(SIM_BUILD_DIR)/$(SIM_TEST)

run-sim: build-sim
	$(SIM_BUILD_DIR)/$(SIM_TARGET)

clean-sim:
	$(RM) $(SIM_BUILD_DIR)
	
## Bento - SDK component
BLACK_FMT:=black
PYTEST:=pytest
SDK_SRC:=sdk
PYTHON:=python

.PHONY: format-sdk clean-sdk build-sdk python-sdk

format-sdk:
	$(BLACK_FMT) $(SDK_SRC)

test-sdk:
	cd $(SDK_SRC) && $(PYTEST)
	
clean-sdk:
	cd $(SDK_SRC) && $(PYTHON) setup.py clean --all

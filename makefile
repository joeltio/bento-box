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
ARCH:=$(shell uname -m)
OS:=$(if $(filter Darwin,$(shell uname -s)),osx,linux)
BIN_DIR:=/usr/local/bin
deps: dep-protoc dev-sdk-dev

PROTOC_VERSION:=3.13.0

dep-protoc: /usr/local/bin/protoc

/usr/local/bin/protoc:
	curl -LO https://github.com/protocolbuffers/protobuf/releases/download/v$(PROTOC_VERSION)/protoc-$(PROTOC_VERSION)-$(OS)-$(ARCH).zip 
	unzip -d /tmp/protoc protoc-$(PROTOC_VERSION)-linux-$(ARCH).zip 
	$(MV) /tmp/protoc/bin/* ${BIN_DIR}
	$(RM) protoc-$(PROTOC_VERSION)-linux-$(ARCH).zip && $(RM) /tmp/protoc

## Bento - Simulator component
SIM_TARGET:=bentobox
SIM_TEST:=bentobox-test
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
SDK_SRC:=sdk
PYTHON:=python
BLACK_FMT:=python -m black
PYTEST:=python -m pytest
PDOC:=python -m pdoc

.PHONY: format-sdk clean-sdk build-sdk build-sdk-docs  dep-sdk-dev test-sdk lint-sdk

dep-sdk-dev:
	pip install -r $(SDK_SRC)/requirements-dev.txt

build-sdk: dep-sdk-dev lint-sdk
	cd $(SDK_SRC) && $(PYTHON) setup.py sdist bdist_wheel

build-sdk-docs: $(SDK_SRC)/docs

$(SDK_SRC)/docs: dep-sdk-dev
	cd $(SDK_SRC) && $(PDOC) --html -o $(notdir $@) bento

format-sdk: dep-sdk-dev
	$(BLACK_FMT) $(SDK_SRC)/bento
	$(BLACK_FMT) $(SDK_SRC)/tests

lint-sdk: dep-sdk-dev
	$(BLACK_FMT) --check $(SDK_SRC)/bento
	$(BLACK_FMT) --check $(SDK_SRC)/tests

test-sdk: dep-sdk-dev
	cd $(SDK_SRC) && $(PYTEST)

clean-sdk:
	cd $(SDK_SRC) && $(PYTHON) setup.py clean --all

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
FIND:=find
CLANG_FMT:=clang-format-11

.PHONY: deps build test clean run
build: build-sim build-sdk

test: test-sim test-sdk

clean: clean-sim clean-sdk

format: format-proto format-sim format-sdk 
	
## Deps: convenience rules for installing dependencies
ARCH:=$(shell uname -m)
OS:=$(if $(filter Darwin,$(shell uname -s)),osx,linux)
BIN_DIR:=/usr/local/bin
deps: dep-protoc dev-sdk-dev dep-clang-fmt dep-sim

PROTOC_VERSION:=3.13.0

dep-protoc: /usr/local/bin/protoc

/usr/local/bin/protoc:
	curl -LO https://github.com/protocolbuffers/protobuf/releases/download/v$(PROTOC_VERSION)/protoc-$(PROTOC_VERSION)-$(OS)-$(ARCH).zip
	unzip -d /tmp/protoc protoc-$(PROTOC_VERSION)-linux-$(ARCH).zip
	$(MV) /tmp/protoc/bin/* ${BIN_DIR}
	$(RM) protoc-$(PROTOC_VERSION)-linux-$(ARCH).zip && $(RM) /tmp/protoc

dep-clang-fmt:
	 wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key|sudo apt-key add -
	 sudo bash -c 'echo "deb http://apt.llvm.org/focal/ llvm-toolchain-focal-11 main\ndeb-src http://apt.llvm.org/focal/ llvm-toolchain-focal-11 main" >/etc/apt/sources.list.d/llvm.list'
	 sudo apt-get update
	 sudo apt-get install -y clang-format-11

## Bento protobuf API
PROTO_SRC := protos
FIND_PROTO_SRC:=$(FIND) $(PROTO_SRC) -type f -name "*.proto"

.PHONY: format-proto lint-proto

format-proto:
	$(FIND_PROTO_SRC) | xargs $(CLANG_FMT) -style=file -i

lint-proto:
	$(FIND_PROTO_SRC) | xargs $(CLANG_FMT) -style=file --dry-run --Werror

## Bento - Simulator component
SIM_TARGET:=bentobox
SIM_TEST:=bentobox-test
SIM_SRC:=sim
SIM_SRC_DIRS:=$(SIM_SRC)/src $(SIM_SRC)/lib/core/src $(SIM_SRC)/lib/core/include $(SIM_SRC)/include
SIM_BUILD_DIR:=sim/build
FIND_SIM_SRC:=$(FIND) $(SIM_SRC_DIRS) -type f \( -name "*.cpp" -o -name "*.h" \)
SIM_BUILD_TYPE:=Release

.PHONY: dep-sim build-sim test-sim run-sim clean-sim format-sim

dep-sim:
	$(CMAKE) -S $(SIM_SRC) -B $(SIM_BUILD_DIR) \
		-D CMAKE_EXPORT_COMPILE_COMMANDS=ON \
		-D CMAKE_BUILD_TYPE=$(SIM_BUILD_TYPE)
	$(CMAKE) --build $(SIM_BUILD_DIR) --parallel $(shell nproc --all) --target deps

build-sim: dep-sim
	$(CMAKE) --build $(SIM_BUILD_DIR) --parallel $(shell nproc --all) \
		--target $(SIM_TARGET) --target $(SIM_TEST)

test-sim: build-sim
	$(SIM_BUILD_DIR)/$(SIM_TEST)

run-sim: build-sim
	$(SIM_BUILD_DIR)/$(SIM_TARGET)

clean-sim:
	$(RM) $(SIM_BUILD_DIR)

format-sim: .clang-format
	$(FIND_SIM_SRC) | xargs $(CLANG_FMT) -style=file -i

lint-sim: .clang-format
	$(FIND_SIM_SRC) | xargs $(CLANG_FMT) -style=file --dry-run --Werror

## Bento - SDK component
SDK_SRC:=sdk
PYTHON:=python
BLACK_FMT:=python -m black
PYTEST:=python -m pytest -vv
PDOC:=python -m pdoc --force

.PHONY: format-sdk clean-sdk build-sdk dep-sdk-dev test-sdk lint-sdk

dep-sdk-dev:
	pip install -r $(SDK_SRC)/requirements-dev.txt

build-sdk: dep-sdk-dev lint-sdk
	cd $(SDK_SRC) && $(PYTHON) setup.py sdist bdist_wheel

format-sdk: dep-sdk-dev
	$(BLACK_FMT) $(SDK_SRC)/bento
	$(BLACK_FMT) $(SDK_SRC)/tests

lint-sdk: dep-sdk-dev
	$(BLACK_FMT) --check $(SDK_SRC)/bento
	$(BLACK_FMT) --check $(SDK_SRC)/tests

test-sdk: dep-sdk-dev
	$(PYTHON) -m pip install -e $(SDK_SRC)
	cd $(SDK_SRC) && $(PYTEST)

clean-sdk:
	cd $(SDK_SRC) && $(PYTHON) setup.py clean --all

# Bento - SDK docs
SDK_DOC_DIR:=$(SDK_SRC)/docs
.PHONY: build-sdk-docs clean-sdk-docs

build-sdk-docs: $(SDK_DOC_DIR)

$(SDK_DOC_DIR): dep-sdk-dev
	$(PDOC) --html -o $(SDK_DOC_DIR) $(SDK_SRC)/bento

clean-sdk-docs: $(SDK_DOC_DIR)
	$(RM) $<

# spellcheck bentobox codebase
.PHONY: spellcheck autocorrect

spellcheck:
	codespell -s

autocorrect:
	codespell -w

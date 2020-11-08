#
# bento-box
# sim component container
# 

FROM ubuntu:20.04 AS build

ENV DEBIAN_FRONTEND=noninteractive
# install build dependencies
RUN apt-get update && apt-get install -y  --no-install-recommends \
    build-essential g++-10 cmake \
    libglfw3-dev xvfb xorg-dev \
    curl ca-certificates unzip \
    # use g++ 10 as compiler
    && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-10 1

ENV PROTOC_VERSION=3.13.0
RUN curl -LO https://github.com/protocolbuffers/protobuf/releases/download/v$PROTOC_VERSION/protoc-$PROTOC_VERSION-linux-x86_64.zip \
    && unzip -d /tmp/protoc protoc-$PROTOC_VERSION-linux-x86_64.zip && mv /tmp/protoc/bin/* /usr/local/bin

# build simlulator
RUN mkdir /repo
COPY makefile /repo/makefile
COPY protos /repo/protos
COPY sim /repo/sim
WORKDIR /repo
RUN make clean-sim && make build-sim

# run simlulator
CMD make run-sim

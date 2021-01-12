#
# bento-box
# sim component container
#

FROM ubuntu:20.04 AS build

ENV DEBIAN_FRONTEND=noninteractive
# setup project dir
RUN mkdir /repo
WORKDIR /repo
# install apt package dependencies
RUN apt-get update && apt-get install -y  --no-install-recommends \
    build-essential g++-10 cmake git \
    libglfw3-dev xvfb xorg-dev \
    ca-certificates \
    # use g++ 10 as compiler
    && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-10 1

# pull build dependencies
COPY makefile /repo/makefile
COPY sim/build/dependencies.cmake /repo/sim/CMakeLists.txt
RUN mkdir -p sim/build
RUN make dep-sim

# build simulator
COPY protos /repo/protos
COPY sim/CMakeLists.txt /repo/sim/CMakeLists.txt
COPY sim/build/dependencies.cmake /repo/sim/dependencies.cmake
COPY sim/lib /repo/sim/lib
COPY sim/src /repo/sim/src
COPY sim/include /repo/sim/include
RUN make build-sim

# run simulator
CMD make run-sim

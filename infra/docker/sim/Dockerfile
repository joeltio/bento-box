#
# bento-box
# sim component container
#

FROM ubuntu:20.04 AS base
ENV DEBIAN_FRONTEND=noninteractive
# install apt runtime dependencies
RUN apt-get update && apt-get install -y  --no-install-recommends \
    libglfw3-dev xvfb xorg-dev ca-certificates

FROM base as build
# setup project dir
RUN mkdir /repo
WORKDIR /repo

# install apt build dependencies
RUN apt-get update && apt-get install -y  --no-install-recommends \
    build-essential g++-10 cmake git ninja-build \
    ca-certificates \
    # use g++ 10 as compiler
    && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-10 1

# pull build dependencies
COPY makefile /repo/makefile
COPY sim/cmake/dependencies.cmake /repo/sim/CMakeLists.txt
RUN mkdir -p sim/build
RUN make dep-sim

# build simulator
COPY protos /repo/protos
COPY sim/CMakeLists.txt /repo/sim/CMakeLists.txt
COPY sim/cmake /repo/sim/cmake
COPY sim/lib /repo/sim/lib
COPY sim/include /repo/sim/include
COPY sim/test_include /repo/sim/test_include
COPY sim/src /repo/sim/src
# do the bulk of the building the simulator
RUN make build-sim
# copy git repository required by sim to obtain version info
# then incremental rebuild to include version info the the build
COPY .git /repo/.git
RUN make build-sim

FROM base as release
# clean apt-get cache
RUN rm -rf /var/lib/apt/lists/* && rm -rf /var/cache/apt/archives/*
# copy built binary into release image
COPY --from=build /repo/sim/build/bentobox /bentobox
# run simulator in virtual framebuffer
CMD xvfb-run -e /dev/stderr /bentobox

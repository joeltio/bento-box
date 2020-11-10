#
# bento-box
# sim component container
# 

FROM ubuntu:20.04 AS build

ENV DEBIAN_FRONTEND=noninteractive
# setup project dir
RUN mkdir /repo
WORKDIR /repo
# install build dependencies
RUN apt-get update && apt-get install -y  --no-install-recommends \
    build-essential g++-10 cmake git \
    libglfw3-dev xvfb xorg-dev \
    # use g++ 10 as compiler
    && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-10 1


# build simulator
COPY makefile /repo/makefile
COPY protos /repo/protos
COPY sim /repo/sim
RUN make clean-sim && make build-sim

# run simlulator
CMD make run-sim

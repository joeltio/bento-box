#
# bento-box
# sim component container
# 

FROM ubuntu:20.04 AS build

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y  --no-install-recommends \
    build-essential g++-10 cmake \
    libglfw3-dev xvfb xorg-dev\
    # use g++ 10 as compiler
    && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-10 1
RUN mkdir /repo
COPY makefile /repo/makefile
COPY sim /repo/sim
WORKDIR /repo
RUN make build-sim
CMD make run-sim

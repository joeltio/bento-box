#
# bento-box
# sim component container
# 

FROM utensils/opengl:20.0.6 AS base

RUN apk add --update --no-cache \
    build-base  \
    cmake \
    glfw-dev \
    g++=10.2.0-r5
RUN mkdir /repo
COPY makefile /repo/makefile
COPY sim /repo/sim
WORKDIR /repo
RUN make build-sim

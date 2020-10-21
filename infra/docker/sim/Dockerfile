#
# bento-box
# sim component container
# 

FROM utensils/opengl:20.0.6 AS base

RUN apk add --update --no-cache build-base cmake clang glfw-dev
RUN mkdir /repo
COPY makefile /repo/makefile
COPY sim /repo/sim
WORKDIR /repo
RUN make build-sim

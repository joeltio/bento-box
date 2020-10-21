#
# bento-box
# sim component container
# 

FROM utensils/opengl:20.0.6 AS base

RUN apk add --update --no-cache build-base cmake clang glfw-dev
COPY . /repo
WORKDIR /repo
RUN make build-sim

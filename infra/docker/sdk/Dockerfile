#
# Bentobox
# SDK container
# 

ARG PY_VERSION=3.7.5
FROM python:$PY_VERSION

# setup project dir
RUN mkdir -p /repo/sdk
WORKDIR /repo

# Install dependencies
COPY makefile /repo/makefile
COPY sdk/requirements-dev.txt /repo/sdk/requirements-dev.txt
RUN make dep-sdk-dev

# build sdk sdist and bdist wheel
COPY protos /repo/protos
COPY sdk /repo/sdk
COPY .git /repo/.git
RUN make clean-sdk lint-sdk build-sdk

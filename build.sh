#!/bin/sh

docker build . -t fridex/thoth-dependency-extract

docker login -u $DOCKER_USER -p $DOCKER_PASS
docker push fridex/thoth-dependency-extract

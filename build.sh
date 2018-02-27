#!/bin/sh

TAG="fridex/thoth-package-extract"
docker build . -t ${TAG}

docker login -u $DOCKER_USER -p $DOCKER_PASS
docker push ${TAG}

#!/bin/bash

SUBSYSTEM_NAME="NodeManager"
DOCKER_IMAGE_NAME="nodemanager"

printf "\n\n"
printf "********************************************************"; \
echo "---------------------- ${SUBSYSTEM_NAME} -------------------------"; \
printf "********************************************************"; \
echo "Deploying ${SUBSYSTEM_NAME}.........."
printf "\n\n"

# path="./nodemanager"
# cd ${path}
# echo $1 | sudo -S docker build . -t ${DOCKER_IMAGE_NAME}:latest;
# echo $1 | sudo -S docker run -d ${DOCKER_IMAGE_NAME}

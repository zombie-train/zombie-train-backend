#!/bin/bash

container_registry="zombietrain.azurecr.io"
name="zombie-train-backend"
version="v1.8.2"

# Set up buildx
docker buildx create --name mybuilder --use

# Build the Docker image
docker buildx build --platform linux/amd64,linux/arm64 -t $container_registry/$name:$version --output type=docker . -f Dockerfile.prod

# Check if the push flag is set
if [ "$1" = "--push" ]; then
    echo "Pushing the image to the registry..."
    az login
    az acr login --name $container_registry
    docker push $container_registry/$name:$version
else
    echo "Image built successfully. Use --push flag to push to registry."
fi

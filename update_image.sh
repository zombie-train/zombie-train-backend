#!/bin/bash

container_registry="zombietrain.azurecr.io"
name="zombie-train-backend"
version="latest"

# Build the Docker image
docker build -t $container_registry/$name:$version . -f Dockerfile.prod

# Check if the push flag is set
if [ "$1" = "--push" ]; then
    echo "Pushing the image to the registry..."
    # if not logged in, log in
    
    az login
    az acr login --name $container_registry
    docker push $container_registry/$name:$version
else
    echo "Image built successfully. Use --push flag to push to registry."
fi

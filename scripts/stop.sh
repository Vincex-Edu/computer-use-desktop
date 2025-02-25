#!/bin/bash

# Move to project root directory (parent of scripts directory)
cd "$(dirname "$0")/.."

# Find and stop any running containers with the computer-use-demo image
CONTAINERS=$(docker ps -q --filter ancestor=computer-use-demo:local)

if [ -z "$CONTAINERS" ]; then
    echo "No running containers found for computer-use-demo:local"

    # Also check for the official image
    CONTAINERS=$(docker ps -q --filter ancestor=ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest)

    if [ -z "$CONTAINERS" ]; then
        echo "No running containers found for the official image either."
        exit 0
    fi
fi

echo "Stopping containers: $CONTAINERS"
docker stop $CONTAINERS
echo "Containers stopped."

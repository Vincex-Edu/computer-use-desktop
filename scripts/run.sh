#!/bin/bash

# Move to project root directory (parent of scripts directory)
cd "$(dirname "$0")/.."

./scripts/setup.sh

# Exit on error
set -e

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create one with your ANTHROPIC_API_KEY."
    exit 1
fi

# Load environment variables from .env file
source .env

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY not found in .env file."
    echo "Please add 'ANTHROPIC_API_KEY=your_api_key' to your .env file."
    exit 1
fi

# Check if Docker image exists, build if it doesn't
if ! docker images | grep -q "computer-use-demo"; then
    echo "Building Docker image..."
    docker build . -t computer-use-demo:local
fi

# Run the Docker container
echo "Starting Anthropic Computer Use Demo..."
docker run \
    -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    -v $(pwd)/computer_use_demo:/home/computeruse/computer_use_demo/ \
    -v $HOME/.anthropic:/home/computeruse/.anthropic \
    -p 5900:5900 \
    -p 8501:8501 \
    -p 6080:6080 \
    -p 8080:8080 \
    -p 7500:7500 \
    -it computer-use-demo:local

echo "Container stopped."

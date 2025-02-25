#!/bin/bash

# Move to project root directory (parent of scripts directory)
cd "$(dirname "$0")/.."

echo "Checking status of Anthropic Computer Use Demo..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check for local image
if docker images | grep -q "computer-use-demo"; then
    echo "✅ Local Docker image found: computer-use-demo:local"
else
    echo "❌ Local Docker image not found. Run './scripts/run.sh' to build it."
fi

# Check for official image
if docker images | grep -q "ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest"; then
    echo "✅ Official Docker image found"
else
    echo "ℹ️ Official Docker image not found locally (will be pulled if needed)"
fi

echo ""
echo "Running containers:"
docker ps --filter ancestor=computer-use-demo:local --filter ancestor=ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest

echo ""
echo "Access URLs (if container is running):"
echo "- Combined interface: http://localhost:8080"
echo "- Streamlit interface: http://localhost:8501"
echo "- Desktop view: http://localhost:6080/vnc.html"
echo "- VNC connection: vnc://localhost:5900"

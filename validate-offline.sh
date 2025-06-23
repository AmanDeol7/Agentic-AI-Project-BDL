#!/bin/bash

# Script to validate offline deployment prerequisites
# This script checks if all required components are available for offline deployment

echo "=== Agentic AI Project - Offline Deployment Validation ==="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
else
    echo "✅ Docker is installed"
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running"
    exit 1
else
    echo "✅ Docker is running"
fi

# Check GPU (for main server)
if command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU detected"
    GPU_AVAILABLE=true
else
    echo "⚠️  No NVIDIA GPU detected (required for main server)"
    GPU_AVAILABLE=false
fi

# Check required Docker images
echo ""
echo "Checking Docker images..."

if docker images --format "table {{.Repository}}:{{.Tag}}" | grep -q "ollama/ollama"; then
    echo "✅ ollama/ollama image found"
else
    echo "❌ ollama/ollama image not found"
    echo "   Run: docker pull ollama/ollama"
fi

if docker images --format "table {{.Repository}}:{{.Tag}}" | grep -q "python:3.12-slim"; then
    echo "✅ python:3.12-slim image found"
else
    echo "❌ python:3.12-slim image not found"
    echo "   Run: docker pull python:3.12-slim"
fi

# Check packages directory
echo ""
echo "Checking offline packages..."
if [ -d "packages" ]; then
    PACKAGE_COUNT=$(ls packages/*.whl 2>/dev/null | wc -l)
    if [ $PACKAGE_COUNT -gt 0 ]; then
        echo "✅ Found $PACKAGE_COUNT Python packages in packages/ directory"
    else
        echo "❌ No wheel files found in packages/ directory"
    fi
else
    echo "❌ packages/ directory not found"
    echo "   Please create packages/ directory and download required Python packages"
fi

# Check if Ollama is running locally and has mistral model
echo ""
echo "Checking Ollama and models..."
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "✅ Ollama is running locally"
    if curl -s http://localhost:11434/api/tags | grep -q "mistral:7b"; then
        echo "✅ mistral:7b model is available"
    else
        echo "⚠️  mistral:7b model not found"
        echo "   Run: ollama pull mistral:7b"
    fi
else
    echo "⚠️  Ollama is not running locally (will be started in Docker)"
fi

echo ""
echo "=== Validation Summary ==="
if [ "$GPU_AVAILABLE" = true ]; then
    echo "✅ Ready for main server deployment (GPU available)"
else
    echo "⚠️  GPU not available - main server deployment may fail"
fi
echo "✅ Ready for client server deployment"
echo ""
echo "To deploy:"
echo "  Main server: ./deploy.sh main"
echo "  Client server: ./deploy.sh client 2"

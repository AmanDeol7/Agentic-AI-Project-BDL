#!/bin/bash

# Offline Deployment script for Agentic AI Project with GPU support
# This script is designed for completely offline environments with pre-downloaded packages
# Prerequisites: Docker, GPU drivers, ollama/ollama image, ubuntu:latest image, mistral:7b model
# Usage: ./deploy.sh [main|client] [client_id]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Function to check GPU availability
check_gpu_available() {
    command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null
}

# Function to check required Docker images for offline deployment
check_offline_requirements() {
    echo "Checking offline deployment requirements..."
    
    # Check if ollama/ollama image exists
    if ! docker images --format "table {{.Repository}}:{{.Tag}}" | grep -q "ollama/ollama"; then
        echo "ERROR: ollama/ollama Docker image not found"
        echo "Please ensure ollama/ollama image is available locally"
        exit 1
    fi
    
    # Check if python:3.12-slim image exists
    if ! docker images --format "table {{.Repository}}:{{.Tag}}" | grep -q "python:3.12-slim"; then
        echo "ERROR: python:3.12-slim Docker image not found"
        echo "Please pull python:3.12-slim image first"
        exit 1
    fi
    
    # Check if packages directory exists
    if [ ! -d "packages" ]; then
        echo "ERROR: packages/ directory not found"
        echo "Please ensure all Python packages are downloaded in packages/ directory"
        exit 1
    fi
    
    echo "✓ Offline requirements validated"
}

SERVER_TYPE=${1:-main}
CLIENT_ID=${2:-1}

echo "Deploying Agentic AI Project..."
echo "Server Type: $SERVER_TYPE"

# Check offline requirements first
check_offline_requirements

case $SERVER_TYPE in
    "main")
        
        
        # Require GPU for main server
        if ! check_gpu_available; then
            echo "ERROR: GPU is required for main server deployment"
            echo "Make sure you have NVIDIA GPU with proper drivers installed"
            exit 1
        fi
        
        echo "GPU detected"
        
        # Check if Docker is running
        if ! docker info &> /dev/null; then
            echo "ERROR: Docker is not running. Please start Docker first."
            exit 1
        fi
        
        # Start main server with GPU support (offline mode)
        cd deployment
        echo "Starting main server containers with GPU acceleration (offline mode)..."
        docker compose -f docker-compose.main-server-gpu-offline.yml up -d
        
        # Wait for Ollama to be ready
        echo "Waiting for Ollama to be ready..."
        sleep 10
        
        # Check if Mistral 7B model is available (skip pull for offline deployment)
        echo "Checking Mistral 7B model availability..."
        if docker exec agentic-ollama-main ollama list | grep -q "mistral:7b"; then
            echo "Mistral 7B model found - ready for offline deployment"
        else
            echo "WARNING: Mistral 7B model not found. Please ensure it's installed via: ollama pull mistral:7b"
        fi
        
        echo "Main server deployed successfully!"
        echo "Backend API: http://localhost:8000"
        echo "Ollama API: http://localhost:11434"
        echo "GPU acceleration: ENABLED"
        ;;
        
    "client")
        if [ -z "$2" ]; then
            echo "ERROR: Client ID is required for client deployment"
            echo "Usage: ./deploy.sh client <client_id>"
            exit 1
        fi
        
        echo "Deploying Client Server #$CLIENT_ID..."
        
        # Check if Docker is running
        if ! docker info &> /dev/null; then
            echo "ERROR: Docker is not running. Please start Docker first."
            exit 1
        fi
        
        # Set environment variables for client
        export CLIENT_ID=$CLIENT_ID
        export FRONTEND_PORT=$((8501 + CLIENT_ID - 1))
        export BACKEND_PORT=$((8001 + CLIENT_ID - 1))
        
        # Prompt for main server URL
        read -p "Enter Main Server URL [http://localhost:8000]: " MAIN_SERVER_INPUT
        export MAIN_SERVER_URL=${MAIN_SERVER_INPUT:-http://localhost:8000}
        
        cd deployment
        echo "Starting client server containers (offline mode)..."
        # Use unique project name for each client to avoid conflicts
        PROJECT_NAME="agentic-client-$CLIENT_ID"
        docker compose -p "$PROJECT_NAME" -f docker-compose.client-server-offline.yml up -d
        
        echo "Client server #$CLIENT_ID deployed successfully!"
        echo "Frontend: http://localhost:$FRONTEND_PORT"
        echo "Backend Proxy: http://localhost:$BACKEND_PORT"
        ;;
        
    *)
        echo "ERROR: Invalid server type. Use 'main' or 'client'"
        echo "Usage: ./deploy.sh [main|client] [client_id]"
        exit 1
        ;;
esac

echo ""
echo "Deployment Summary:"
echo "  - Server Type: $SERVER_TYPE"
if [ "$SERVER_TYPE" = "main" ]; then
    echo "  - GPU Support: ENABLED"
    echo ""
    echo "Check logs: docker compose -f deployment/docker-compose.main-server-gpu-offline.yml logs -f"
    echo "Stop: docker compose -f deployment/docker-compose.main-server-gpu-offline.yml down"
fi
if [ "$SERVER_TYPE" = "client" ]; then
    echo "  - Client ID: $CLIENT_ID"
    echo "  - Frontend Port: $FRONTEND_PORT"
    echo "  - Backend Port: $BACKEND_PORT"
    echo "  - Main Server: $MAIN_SERVER_URL"
    echo ""
    echo "Check logs: docker compose -p agentic-client-$CLIENT_ID -f deployment/docker-compose.client-server-offline.yml logs -f"
    echo "Stop: docker compose -p agentic-client-$CLIENT_ID -f deployment/docker-compose.client-server-offline.yml down"
fi

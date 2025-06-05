#!/bin/bash

# Deployment script for Agentic AI Project with GPU support
# Usage: ./deploy.sh [main|client] [client_id]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Function to check GPU availability
check_gpu_available() {
    command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null
}

SERVER_TYPE=${1:-main}
CLIENT_ID=${2:-1}

echo "Deploying Agentic AI Project..."
echo "Server Type: $SERVER_TYPE"

case $SERVER_TYPE in
    "main")
        echo "Deploying Main Server with LLaMA 3.2 1B..."
        
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
        
        # Start main server with GPU support
        cd deployment
        echo "Starting main server containers with GPU acceleration..."
        docker compose -f docker-compose.main-server-gpu.yml up -d
        
        # Wait for Ollama to be ready
        echo "Waiting for Ollama to be ready..."
        sleep 10
        
        # Pull Mistral 7B model
        echo "Pulling Mistral 7B model..."
        docker exec agentic-ollama-main ollama pull mistral:7b
        
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
        echo "Starting client server containers..."
        docker compose -f docker-compose.client-server.yml up -d
        
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
    echo "Check logs: docker compose -f deployment/docker-compose.main-server-gpu.yml logs -f"
    echo "Stop: docker compose -f deployment/docker-compose.main-server-gpu.yml down"
fi
if [ "$SERVER_TYPE" = "client" ]; then
    echo "  - Client ID: $CLIENT_ID"
    echo "  - Frontend Port: $FRONTEND_PORT"
    echo "  - Backend Port: $BACKEND_PORT"
    echo "  - Main Server: $MAIN_SERVER_URL"
    echo ""
    echo "Check logs: docker compose -f deployment/docker-compose.client-server.yml logs -f"
    echo "Stop: docker compose -f deployment/docker-compose.client-server.yml down"
fi

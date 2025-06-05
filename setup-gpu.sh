#!/bin/bash

# GPU Setup Helper Script for Agentic AI Project
# This script helps set up NVIDIA GPU support for Docker

set -e

echo "🔧 GPU Setup Helper for Agentic AI Project"
echo "=========================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run this script as root"
    echo "   Run it as your regular user, it will ask for sudo when needed"
    exit 1
fi

# Check for NVIDIA GPU
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ nvidia-smi not found. Please install NVIDIA drivers first."
    echo "   Visit: https://www.nvidia.com/drivers"
    exit 1
fi

echo "✅ NVIDIA GPU detected:"
nvidia-smi --query-gpu=name,driver_version --format=csv,noheader

# Check Docker installation
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker detected:"
docker --version

# Check if user is in docker group
if ! groups $USER | grep -q docker; then
    echo "⚠️  User $USER is not in the docker group"
    echo "   Adding user to docker group..."
    sudo usermod -aG docker $USER
    echo "   ⚠️  You'll need to log out and log back in for this to take effect"
fi

# Check if nvidia-container-toolkit is installed
if ! command -v nvidia-container-runtime &> /dev/null && ! dpkg -l | grep -q nvidia-container-toolkit; then
    echo "🔧 Installing nvidia-container-toolkit..."
    
    # Add NVIDIA package repository
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    
    # Install the toolkit
    sudo apt-get update
    sudo apt-get install -y nvidia-container-toolkit
    
    # Configure Docker to use nvidia runtime
    sudo nvidia-ctk runtime configure --runtime=docker
    
    echo "🔄 Restarting Docker service..."
    sudo systemctl restart docker
    
    echo "✅ nvidia-container-toolkit installed and configured"
else
    echo "✅ nvidia-container-toolkit already installed"
fi

# Test Docker GPU access
echo "🧪 Testing Docker GPU access..."

if docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi &> /dev/null; then
    echo "✅ Docker GPU access with --gpus flag works!"
elif docker run --rm --runtime=nvidia nvidia/cuda:11.0-base nvidia-smi &> /dev/null; then
    echo "✅ Docker GPU access with --runtime=nvidia works!"
else
    echo "❌ Docker GPU access failed"
    echo "   Trying to restart Docker daemon..."
    sudo systemctl restart docker
    sleep 5
    
    if docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi &> /dev/null; then
        echo "✅ Docker GPU access works after restart!"
    else
        echo "❌ Still failing. Manual investigation needed."
        echo "   Check Docker daemon logs: sudo journalctl -u docker.service"
        exit 1
    fi
fi

echo ""
echo "🎉 GPU setup complete!"
echo "   You can now run: ./deploy.sh main"
echo ""
echo "💡 If you added the user to docker group, remember to:"
echo "   1. Log out and log back in, OR"
echo "   2. Run: newgrp docker"

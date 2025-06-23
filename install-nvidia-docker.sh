#!/bin/bash

# NVIDIA Container Runtime Installation Script
# For fresh Linux systems with Docker already installed
# This script installs NVIDIA Container Runtime for GPU support in Docker

set -e

echo "=== NVIDIA Container Runtime Installation ==="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
else
    echo "✅ Docker is installed"
fi

# Check if NVIDIA drivers are installed
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ NVIDIA drivers not found. Please install NVIDIA drivers first."
    echo "   Run: sudo apt update && sudo apt install nvidia-driver-535"
    exit 1
else
    echo "✅ NVIDIA drivers found"
    nvidia-smi --query-gpu=name --format=csv,noheader
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
else
    echo "❌ Cannot detect OS version"
    exit 1
fi

echo "Detected OS: $OS $VERSION"

# Install NVIDIA Container Runtime based on OS
case $OS in
    "ubuntu")
        echo "Installing NVIDIA Container Runtime for Ubuntu..."
        
        # Add NVIDIA package repository
        curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
        curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
            sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
            sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
        
        # Update package list
        sudo apt-get update
        
        # Install NVIDIA Container Toolkit
        sudo apt-get install -y nvidia-container-toolkit
        ;;
        
    "centos"|"rhel"|"fedora")
        echo "Installing NVIDIA Container Runtime for RHEL/CentOS/Fedora..."
        
        # Add NVIDIA repository
        curl -s -L https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo | \
            sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo
        
        # Install NVIDIA Container Toolkit
        sudo yum install -y nvidia-container-toolkit
        ;;
        
    *)
        echo "❌ Unsupported OS: $OS"
        echo "Please install NVIDIA Container Runtime manually:"
        echo "https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
        exit 1
        ;;
esac

# Configure Docker to use NVIDIA runtime
echo "Configuring Docker for NVIDIA runtime..."
sudo nvidia-ctk runtime configure --runtime=docker

# Restart Docker service
echo "Restarting Docker service..."
sudo systemctl restart docker

# Wait for Docker to restart
sleep 3

# Test GPU access
echo ""
echo "Testing GPU access in Docker..."
if sudo docker run --rm --gpus all nvidia/cuda:11.0-base-ubuntu20.04 nvidia-smi; then
    echo ""
    echo "🎉 SUCCESS! NVIDIA Container Runtime installed and working!"
    echo ""
    echo "You can now deploy the Agentic AI Project with GPU support:"
    echo "  ./deploy.sh main"
else
    echo ""
    echo "❌ GPU test failed. Please check the installation."
    echo "Try rebooting the system and running the test again."
fi

echo ""
echo "=== Installation Complete ==="

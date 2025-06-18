#!/bin/bash

# This script gathers Docker Engine and Docker Desktop packages for offline installation

set -e

echo "📦 Creating directory docker-offline-packages..."
mkdir -p docker-offline-packages/docker-debs

echo "🌐 Adding Docker GPG key and repo (Ubuntu 24.04 - noble)..."
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o docker.gpg
sudo install -o root -g root -m 644 docker.gpg /etc/apt/trusted.gpg.d/docker.gpg

echo "deb [arch=amd64] https://download.docker.com/linux/ubuntu noble stable" | sudo tee /etc/apt/sources.list.d/docker.list

sudo apt-get update

echo "⬇️ Downloading Docker .deb packages..."
cd docker-offline-packages/docker-debs
apt download docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
cd ../..

echo "⬇️ Downloading Docker Desktop..."
wget https://desktop.docker.com/linux/main/amd64/docker-desktop-4.30.0-amd64.deb -O docker-offline-packages/docker-desktop-4.30.0-amd64.deb

echo "🗜️ Creating docker-offline-bundle.zip..."
zip -r docker-offline-bundle.zip docker-offline-packages

echo "✅ Done. Transfer docker-offline-bundle.zip to your offline machine."

    # Complete Deployment Guide for Agentic AI Project

## Prerequisites

Before deploying, ensure you have:

1. **Docker and Docker Compose** installed
2. **NVIDIA GPU** with NVIDIA Docker runtime (optional but recommended for GPU acceleration)
3. **8GB+ RAM** available
4. **Sufficient disk space** (~10GB for models and containers)

### GPU Support (Recommended)

For optimal performance, this project supports NVIDIA GPU acceleration:

**Check GPU Availability:**
```bash
# Check if NVIDIA GPU is available
nvidia-smi

# Check if NVIDIA Docker runtime is installed
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

**Install NVIDIA Docker Support (if needed):**
```bash
# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

### Check Prerequisites

```bash
# Check Docker
docker --version
docker compose version

# Check NVIDIA Docker (if using GPU)
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# Check available resources
free -h
df -h
```

## Step-by-Step Deployment

### Option 1: Automated Deployment (Recommended)

#### Step 1: Navigate to Project Directory
```bash
cd /home/aman/Desktop/intern-taask-bdl/Agentic-AI-Project-BDL
```

#### Step 2: Make Scripts Executable
```bash
chmod +x deploy.sh

```

#### Step 3: Deploy Main Server
```bash
# Deploy the main server with Mistral 7B model
./deploy.sh main
```

This will:
- ✅ Install Ollama if not present
- ✅ Start Docker containers (Ollama + Backend API)
- ✅ Pull Mistral 7B model (~4.1GB download)
- ✅ Expose services on:
  - Backend API: `http://localhost:8000`
  - Ollama API: `http://localhost:11434`

#### Step 4: Deploy Client Server(s)
```bash
# Deploy first client server
./deploy.sh client 1

# Deploy additional clients (optional)
./deploy.sh client 2
./deploy.sh client 3
```

Each client will:
- ✅ Ask for main server URL (default: `http://localhost:8000`)
- ✅ Start on unique ports:
  - Client 1: Frontend `http://localhost:8501`, Backend Proxy `http://localhost:8001`
  - Client 2: Frontend `http://localhost:8502`, Backend Proxy `http://localhost:8002`
  - And so on...

### Option 2: Simple Deployment (No Redis/Nginx)

If you prefer the simplified version:

```bash
# Deploy main server (simple)
./deploy-simple.sh main

# Deploy client server (simple)
./deploy-simple.sh client 1
```

### Option 3: Manual Deployment

If you want full control over the deployment:

#### Step 1: Deploy Main Server Manually
```bash
cd deployment

# Start main server containers
docker compose -f docker-compose.main-server.yml up -d

# Wait for containers to start
sleep 15

# Pull the Mistral model
docker exec agentic-ollama-main ollama pull mistral:7b
```

#### Step 2: Deploy Client Server Manually
```bash
# Set environment variables for client
export CLIENT_ID=1
export FRONTEND_PORT=8501
export BACKEND_PORT=8001
export MAIN_SERVER_URL=http://localhost:8000

# Start client containers
docker compose -f docker-compose.client-server.yml up -d
```

## Verification and Testing

### 1. Check Container Status
```bash
# Check all containers are running
docker ps

# Should see containers like:
# - agentic-ollama-main
# - agentic-backend-main
# - agentic-frontend-client-1
# - agentic-backend-proxy-1
```

### 2. Test Services

#### Test Main Server
```bash
# Test backend API health
curl http://localhost:8000/health

# Test Ollama API
curl http://localhost:11434/api/tags
```

#### Test Client Server
```bash
# Test frontend (should return HTML)
curl http://localhost:8501

# Test backend proxy
curl http://localhost:8001/health
```

### 3. Test AI Functionality
```bash
# Test Ollama model directly
curl http://localhost:11434/api/generate -d '{
  "model": "mistral:7b",
  "prompt": "Hello, how are you?",
  "stream": false
}'
```

### 4. Access the Application

1. **Open your web browser**
2. **Navigate to**: `http://localhost:8501` (Client 1)
3. **Try uploading a document** and asking questions
4. **Test code generation** and execution

## Monitoring and Logs

### View Container Logs
```bash
# Main server logs
cd deployment
docker compose -f docker-compose.main-server.yml logs -f

# Client server logs
docker compose -f docker-compose.client-server.yml logs -f

# Individual container logs
docker logs agentic-ollama-main -f
docker logs agentic-backend-main -f
```

### Monitor Resources
```bash
# Monitor container resource usage
docker stats

# Check GPU usage (if using GPU)
nvidia-smi
```

## Stopping the Application

### Stop All Services
```bash
cd deployment

# Stop main server
docker compose -f docker-compose.main-server.yml down

# Stop client servers
docker compose -f docker-compose.client-server.yml down
```

### Stop and Remove Everything (Clean Shutdown)
```bash
# Stop and remove containers, networks, and volumes
docker compose -f docker-compose.main-server.yml down -v
docker compose -f docker-compose.client-server.yml down -v

# Clean up Docker system (optional)
docker system prune -f
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   sudo netstat -tulpn | grep :8000
   
   # Kill the process or change ports in environment variables
   ```

2. **GPU Not Detected**
   ```bash
   # Install NVIDIA Docker runtime
   sudo apt-get update
   sudo apt-get install -y nvidia-docker2
   sudo systemctl restart docker
   ```

3. **Model Download Fails**
   ```bash
   # Manually pull the model
   docker exec -it agentic-ollama-main ollama pull mistral:7b
   ```

4. **Connection Issues**
   ```bash
   # Check Docker networks
   docker network ls
   docker network inspect deployment_agentic-network
   ```

5. **Memory Issues**
   ```bash
   # Check available memory
   free -h
   
   # If low memory, try smaller model
   docker exec agentic-ollama-main ollama pull phi3
   ```

### Health Checks

Create a simple health check script:

```bash
#!/bin/bash
echo "🔍 Checking Agentic AI Application Health..."

# Check containers
echo "📦 Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check services
echo -e "\n🌐 Service Health:"
echo "Main Backend: $(curl -s http://localhost:8000/health || echo 'FAILED')"
echo "Ollama API: $(curl -s http://localhost:11434/api/tags || echo 'FAILED')"
echo "Client Frontend: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8501 || echo 'FAILED')"
echo "Client Backend: $(curl -s http://localhost:8001/health || echo 'FAILED')"

echo -e "\n✅ Health check complete!"
```

## Quick Commands Reference

```bash
# Deploy everything
./deploy.sh main && ./deploy.sh client 1

# Check status
docker ps

# View logs
docker compose -f deployment/docker-compose.main-server.yml logs -f

# Stop everything
docker compose -f deployment/docker-compose.main-server.yml down
docker compose -f deployment/docker-compose.client-server.yml down

# Access application
# Browser: http://localhost:8501
```

Your Agentic AI application should now be fully deployed and accessible!

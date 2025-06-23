# Offline Deployment Guide

This guide covers deploying the Agentic AI Project in completely offline environments where internet access is not available.

## Prerequisites

### System Requirements
- **GPU**: NVIDIA GPU with proper drivers (for main server)
- **Docker**: Docker Engine installed and running
- **Storage**: At least 20GB free space

### Pre-downloaded Components
Before deploying offline, ensure you have:

1. **Docker Images**:
   ```bash
   docker pull ollama/ollama:latest
   docker pull python:3.12-slim
   ```

2. **Python Packages**: All required packages downloaded as wheel files in `packages/` directory

3. **AI Model**: Mistral 7B model available locally via Ollama:
   ```bash
   ollama pull mistral:7b
   ```

## Validation

Run the validation script to check if all prerequisites are met:

```bash
./validate-offline.sh
```

This will check:
- ✅ Docker installation and status
- ✅ GPU availability (for main server)
- ✅ Required Docker images
- ✅ Python packages in `packages/` directory
- ✅ Mistral 7B model availability

## Deployment

### 1. Main Server (GPU Required)

Deploy the main AI server with GPU acceleration:

```bash
./deploy.sh main
```

This will:
- Start Ollama container with GPU support
- Start backend API server
- Use pre-downloaded packages for installation
- Skip model download (uses existing mistral:7b)

**Ports:**
- Backend API: `http://localhost:8000`
- Ollama API: `http://localhost:11434`

### 2. Client Servers

Deploy additional client instances:

```bash
./deploy.sh client 2    # Deploy Client 2
./deploy.sh client 3    # Deploy Client 3
```

Each client will:
- Start on unique ports (850X for frontend, 800X for backend)
- Connect to main server for AI processing
- Use session isolation for multi-user support

**Example Client 2:**
- Frontend: `http://localhost:8502`
- Backend Proxy: `http://localhost:8002`

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client 2      │    │   Client 3      │    │   Client N      │
│ (Port 8502)     │    │ (Port 8503)     │    │ (Port 850N)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Main Server    │
                    │  (Port 8000)    │
                    │                 │
                    │ ┌─────────────┐ │
                    │ │ Ollama LLM  │ │
                    │ │ (GPU Accel) │ │
                    │ └─────────────┘ │
                    └─────────────────┘
```

## Offline-Specific Features

### 1. Package Installation
- Uses `--no-index --find-links packages/` for pip installation
- No internet connectivity required during container build
- All dependencies resolved from local wheel files

### 2. Model Management
- Skips `ollama pull` commands
- Uses pre-installed mistral:7b model
- Validates model availability before deployment

### 3. Container Configuration
- Uses offline-specific Dockerfiles (`*-offline`)
- Optimized for air-gapped environments
- Includes offline health checks

## File Structure

```
Agentic-AI-Project-BDL/
├── deploy.sh                          # Main deployment script
├── validate-offline.sh                # Prerequisites validation
├── packages/                          # Pre-downloaded Python packages
│   ├── fastapi-*.whl
│   ├── streamlit-*.whl
│   └── ...
├── deployment/
│   ├── Dockerfile.backend-offline     # Offline backend Dockerfile
│   ├── Dockerfile.frontend-offline    # Offline frontend Dockerfile
│   ├── docker-compose.main-server-gpu-offline.yml
│   └── docker-compose.client-server-offline.yml
```

## Troubleshooting

### GPU Issues
```bash
# Check GPU availability
nvidia-smi

# Verify Docker GPU support
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

### Package Issues
```bash
# Verify packages directory
ls -la packages/

# Check package count
ls packages/*.whl | wc -l
```

### Model Issues
```bash
# Check if mistral:7b is available
docker exec agentic-ollama-main-offline ollama list
```

### Container Logs
```bash
# Main server logs
docker compose -f deployment/docker-compose.main-server-gpu-offline.yml logs -f

# Client logs
docker compose -p agentic-client-2 -f deployment/docker-compose.client-server-offline.yml logs -f
```

## Stopping Services

### Stop Main Server
```bash
docker compose -f deployment/docker-compose.main-server-gpu-offline.yml down
```

### Stop Client Server
```bash
docker compose -p agentic-client-2 -f deployment/docker-compose.client-server-offline.yml down
```

## Security Considerations

- All processing happens locally (no external API calls)
- Session isolation between clients
- Sandboxed code execution environment
- No internet connectivity required after deployment

## Performance Optimization

- GPU acceleration for AI inference
- Local model caching
- Optimized Docker layer caching for offline builds
- Session-based resource management

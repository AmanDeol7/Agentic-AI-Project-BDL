# Quick Start Guide

## Prerequisites
- NVIDIA GPU (required for main server)
- Docker & Docker Compose
- Ubuntu/Linux system with sudo access

## 1-Minute Deployment

```bash
# Clone and enter directory
git clone <repository-url>
cd Agentic-AI-Project-BDL

# Make script executable
chmod +x deploy.sh

# Deploy main server (requires GPU)
sudo ./deploy.sh main

# Deploy client instances for multiple users
sudo ./deploy.sh client 2
sudo ./deploy.sh client 3
sudo ./deploy.sh client 4
```

## Access Your Application

| Service | URL | Purpose |
|---------|-----|---------|
| **Client 2** | http://localhost:8502 | User interface |
| **Client 3** | http://localhost:8503 | User interface |
| **Client 4** | http://localhost:8504 | User interface |
| **Main API** | http://localhost:8000/docs | API documentation |
| **Ollama** | http://localhost:11434 | LLM backend |

## Test the System

1. **Open** http://localhost:8502 in your browser
2. **Upload** a document (PDF, Excel, Word, or text)
3. **Ask** questions about the document
4. **Try** code generation: "Write a Python function to sort a list"
5. **Test** session isolation by opening http://localhost:8503 in a new browser

## Key Features Working

**Multi-Client Support**: Isolated sessions for concurrent users  
**GPU Acceleration**: Fast inference with NVIDIA GPU  
**Document Analysis**: PDF, Excel, Word, text file processing  
**Code Generation**: Python, C, C++ with execution support  
**Session Management**: Advanced session control and monitoring  
**File Isolation**: Session-specific file uploads and processing  

## Quick Commands

```bash
# Check status
docker ps

# View logs
sudo docker logs agentic-backend-main -f

# Stop everything
sudo docker compose -f deployment/docker-compose.main-server-gpu.yml down
sudo docker compose -p agentic-client-2 -f deployment/docker-compose.client-server.yml down

# Restart a client
sudo ./deploy.sh client 2
```

## Need Help?

- **Full Guide**: [README.md](README.md)
- **Deployment**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)  
- **Multi-Client**: [MULTI_CLIENT_USAGE_GUIDE.md](MULTI_CLIENT_USAGE_GUIDE.md)
- **Issues**: Check logs with `sudo docker logs <container-name>`

**You're ready to go!** Start chatting with your AI assistant and enjoy the multi-client capabilities!

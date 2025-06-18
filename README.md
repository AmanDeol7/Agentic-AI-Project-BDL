# Agentic AI Project

A sophisticated multi-agent AI system for code generation and document analysis using local language models with GPU acceleration and multi-client session support.

> **Quick Start**: New to this project? Check out [QUICK_START.md](QUICK_START.md) for 1-minute deployment!

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)
[![GPU](https://img.shields.io/badge/GPU-NVIDIA-green.svg)](https://developer.nvidia.com/cuda-downloads)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

### Core Capabilities
- **Code Agent**: Generates, analyzes, and executes Python, C, and C++ code with intelligent error handling
- **Document Agent**: Advanced analysis of PDF, Excel, Word, and text files with RAG capabilities
- **Smart Routing**: Automatically routes queries to the most appropriate agent based on context
- **Multi-Modal Support**: Handle both text and file inputs seamlessly

### Technical Features
- **Local LLM Support**: Ollama integration (Mistral 7B, LLaMA 3.2, CodeLlama)
- **GPU Acceleration**: NVIDIA GPU support for faster inference (required for main server)
- **Multi-Client Architecture**: Isolated sessions for multiple simultaneous users
- **Session Management**: Advanced session isolation and management system
- **RESTful API**: FastAPI backend for integration with external systems
- **Modern UI**: Streamlit-based interface with real-time session management

### Deployment Options
- **Local Development**: Single-command setup for development and testing
- **Docker Deployment**: Production-ready containerized deployment with GPU support
- **Multi-Client Architecture**: Scale with isolated client instances supporting concurrent users
- **Session Management**: Advanced session isolation for enterprise-grade multi-user support
- **GPU Support**: Automatic GPU detection and utilization for optimal performance

## Quick Start

### Option 1: Production Docker Deployment (Recommended)
Perfect for production use with multi-client support:

```bash
# Clone the repository
git clone <repository-url>
cd Agentic-AI-Project-BDL

# Make deployment script executable
chmod +x deploy.sh

# Deploy main server with GPU support (required)
sudo ./deploy.sh main

# Deploy multiple client instances for concurrent users
sudo ./deploy.sh client 2
sudo ./deploy.sh client 3
sudo ./deploy.sh client 4
# ... add as many clients as needed
```

**Access Points:**
- **Client 2**: `http://localhost:8502` (Frontend), `http://localhost:8002` (Backend Proxy)
- **Client 3**: `http://localhost:8503` (Frontend), `http://localhost:8003` (Backend Proxy)
- **Client N**: `http://localhost:850(N)` (Frontend), `http://localhost:800(N)` (Backend Proxy)
- **Main Server API**: `http://localhost:8000/docs` (Documentation)
- **Ollama API**: `http://localhost:11434`

### Option 2: Local Development
For development and testing:

```bash
# Clone the repository
git clone <repository-url>
cd Agentic-AI-Project-BDL

# Automated setup (installs dependencies and starts Ollama)
python setup-dev.py



#for bdl use 
# create and activate venv
python3 -m venv venv
source myenv/bin/activate


#download wheel files 
pip download -r requirements.txt -d ./packages


#install on machine
pip install --no-index --find-links=./packages -r requirements.txt



# Launch the application
ollama serve
uvicorn backend.api_server:app --host 0.0.0.0 --port 8000
streamlit run main.py

```

### Option 3: API-Only Mode
For integration with existing applications:

```bash
# Start only the backend API
uvicorn backend.api_server:app --host 0.0.0.0 --port 8000

# Test the API
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -H "x-session-id: test-session" \
  -H "x-client-id: test-client" \
  -d '{"message": "Generate a Python function to calculate fibonacci numbers"}'
```

## Requirements

### System Requirements
- **Python**: 3.12+ (for local development)
- **NVIDIA GPU**: Required for main server deployment (GTX 1060+ or RTX series recommended)
- **Memory**: 8GB+ RAM (16GB recommended for optimal performance)
- **Storage**: ~10GB free space (for models and containers)
- **OS**: Linux, macOS, or Windows with WSL2

### Essential Dependencies
- **Docker & Docker Compose**: Required for production deployment
- **NVIDIA Docker Runtime**: Required for GPU acceleration
- **CUDA**: Version 11.0+ (automatically handled in Docker)

### Quick System Check
```bash
# Verify Python version
python --version

# Check GPU availability (required for main server)
nvidia-smi

# Check Docker installation
docker --version && docker compose version

# Verify NVIDIA Docker support
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# Check available memory
free -h  # Linux/macOS
wmic computersystem get TotalPhysicalMemory  # Windows

# Check disk space
df -h
```

## Architecture

### Multi-Client System Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Client 2 UI    │    │  Client 3 UI    │    │  Client N UI    │
│  (Port 8502)    │    │  (Port 8503)    │    │  (Port 850N)    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Backend Proxy 2 │    │ Backend Proxy 3 │    │ Backend Proxy N │
│  (Port 8002)    │    │  (Port 8003)    │    │  (Port 800N)    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 ▼
                    ┌─────────────────┐    ┌─────────────────┐
                    │ Main Server API │◄──►│   Ollama LLM    │
                    │  (Port 8000)    │    │  (Port 11434)   │
                    └─────────────────┘    └─────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Session Manager │
                    │ (Multi-Client)  │
                    └─────────────────┘
```

### Session Isolation Features
- **Independent Sessions**: Each client gets isolated conversation contexts
- **File Separation**: Session-specific upload directories (`/data/uploads/session_{id}/`)
- **Assistant Isolation**: Separate AI assistant instances per session
- **Resource Management**: Automatic session cleanup and timeout handling

### Agent System
- **Agent Router**: Intelligently routes queries based on content analysis
- **Code Agent**: Specializes in code generation, analysis, and execution
- **Document Agent**: Handles file processing, summarization, and Q&A
- **Tool Integration**: Extensible tool system for specialized tasks

### Deployment Modes
1. **Multi-Client Production**: Centralized backend with multiple isolated client frontends
2. **Local Development**: All components on a single machine for development
3. **API-Only**: Backend service for external integration and custom frontends

## Multi-Client Support

### Key Features
- **Session Isolation**: Complete separation between different client sessions
- **Concurrent Users**: Support unlimited simultaneous users with isolated contexts
- **File Separation**: Session-specific file uploads and processing
- **Independent Conversations**: Each client maintains separate chat history
- **Session Management**: Advanced UI for session control and monitoring
- **Automatic Cleanup**: Session timeout and resource management

### Use Cases
```bash
# Team Development
Team Lead:        http://localhost:8502
Frontend Dev:     http://localhost:8503  
Backend Dev:      http://localhost:8504
QA Engineer:      http://localhost:8505

# Multi-Project Work
Project Alpha:    http://localhost:8502
Project Beta:     http://localhost:8503
Research:         http://localhost:8504

# Training & Demos
Instructor:       http://localhost:8502
Student 1:        http://localhost:8503
Student 2:        http://localhost:8504
```

## Project Structure

```
Agentic-AI-Project-BDL/
├── main.py                       # Local application entry point
├── setup-dev.py                  # Development setup script  
├── deploy.sh                     # Docker deployment script (use with sudo)
├── README.md                     # This file - project overview
├── DEPLOYMENT_GUIDE.md           # Detailed deployment instructions
├── MULTI_CLIENT_USAGE_GUIDE.md   # Multi-client setup and usage
├── MULTI_CLIENT_SESSION_SUMMARY.md # Implementation details
├── backend/
│   ├── agents/                   # AI agent implementations
│   │   ├── base_agent.py            # Base agent class
│   │   ├── code_agent.py            # Code generation & analysis
│   │   └── doc_agent.py             # Document processing
│   ├── tools/                    # Specialized tools
│   │   ├── code_tools/              # Code execution & analysis
│   │   └── doc_tools/               # Document processing tools
│   ├── llm_providers/            # LLM integrations
│   │   ├── ollama_provider.py       # Ollama integration
│   │   └── tensorrt_provider.py     # TensorRT-LLM support
│   ├── graphs/                   # Workflow orchestration
│   │   └── agent_controller.py      # LangGraph controller
│   ├── utils/                    # Utilities
│   │   ├── memory.py                # Memory management
│   │   ├── router.py                # Request routing
│   │   └── session_manager.py       # Multi-client session management
│   └── api_server.py             # FastAPI backend server
├── frontend/
│   ├── app.py                       # Standalone Streamlit app
│   ├── client_app.py                # Multi-client frontend
│   ├── session_manager_app.py       # Session management interface
│   └── components/                  # Reusable UI components
│       ├── chat_interface.py        # Chat UI with session support
│       ├── file_uploader.py         # File upload component
│       └── session_manager.py       # Session management UI
├── config/                       # Configuration files
│   ├── app_config.py                # Main application config
│   └── llm_config.py                # LLM-specific settings
├── deployment/                   # Docker configurations
│   ├── docker-compose.*.yml         # Various deployment configs
│   ├── Dockerfile.*                 # Service-specific Dockerfiles
│   └── scripts/                     # Deployment scripts
└── data/                         # Data storage
    └── uploads/                     # User uploaded files
        └── session_{id}/            # Session-specific file isolation
```

### Key Components
- **Agent System**: Modular AI agents with specialized capabilities
- **Tool Integration**: Extensible tool system for code execution and document processing  
- **LLM Providers**: Support for multiple language model backends
- **Workflow Engine**: LangGraph-based orchestration for complex tasks
- **API Layer**: RESTful API for external integrations

## Configuration & Customization

### Model Selection

The system supports multiple LLM models via Ollama. Edit `config/app_config.py`:

```python
LLM_CONFIG = {
    "provider": "ollama",
    "model": "mistral:7b",        # Default: balanced performance
    "temperature": 0.7,           # Creativity level (0.0-1.0)
    "max_tokens": 1000           # Response length limit
}
```

**Available Models:**
| Model | Size | Best For | Performance |
|-------|------|----------|-------------|
| `mistral:7b` | ~4.1GB | General tasks, balanced | ⭐⭐⭐⭐ |
| `llama3.2:1b` | ~1.3GB | Quick responses, low memory | ⭐⭐⭐ |
| `llama3.2:3b` | ~2.0GB | Good balance | ⭐⭐⭐⭐ |
| `codellama:7b` | ~3.8GB | Code generation | ⭐⭐⭐⭐⭐ |

### Install a New Model
```bash
# Pull model (will download automatically)
ollama pull llama3.2:3b

# Update config and restart application
# Local: python main.py
# Docker: ./deploy.sh main
```

### Environment Variables
```bash
# Application settings
export STREAMLIT_PORT=8501
export API_PORT=8000
export OLLAMA_HOST=localhost:11434

# GPU settings (optional)
export CUDA_VISIBLE_DEVICES=0
export NVIDIA_VISIBLE_DEVICES=all

# Deployment mode
export SERVER_TYPE=standalone  # or 'client' for client-server
export MAIN_SERVER_URL=http://localhost:8000  # for client mode
```

### Advanced Configuration
For production deployments, see the [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for:
- Multi-client scaling
- GPU optimization 
- Network configuration
- Security settings

## Usage Examples

### Code Generation
```
User: "Create a Python function to analyze sentiment of text using transformers"

AI Response:
- Code generated and tested
- Dependencies identified  
- Example usage provided
- Error handling included
```

### Document Analysis
```
Upload: business_report.pdf (2.3MB)
Query: "What are the key financial metrics mentioned?"

AI Response:
- Revenue: $2.4M (↑15% YoY)
- Profit Margin: 18.5%
- Cash Flow: $450K positive
- Full summary with page references
```

### Multi-Agent Workflow
```
Query: "Analyze this CSV file and create a visualization script"

Process:
1. Document Agent: Parses CSV structure  
2. Router: Determines need for both agents
3. Code Agent: Generates matplotlib script
4. Result: Working visualization code + data insights
```

### API Integration
```python
import requests

# Chat with the AI
response = requests.post("http://localhost:8000/chat", json={
    "message": "Generate a REST API using FastAPI",
    "agent": "code"  # Optional: specify agent
})

print(response.json()["response"])
```

## Development Workflow

### Setting Up Development Environment
```bash
# Clone and setup
git clone <repository-url>
cd Agentic-AI-Project-BDL

# Install in development mode
pip install -e .
pip install -r requirements.txt

# Install pre-commit hooks (optional)
pre-commit install

# Start development server with auto-reload
python main.py --dev
```

### Adding New Agents
```python
# Create new agent in backend/agents/
from .base_agent import BaseAgent

class CustomAgent(BaseAgent):
    def process_request(self, context):
        # Your agent logic here
        return response

# Register in agent_controller.py
agents = {
    "custom": CustomAgent(),
    # ... existing agents
}
```

### Testing
```bash
# Run all tests
python -m pytest tests/

# Run specific test category
python -m pytest tests/test_agents.py
python -m pytest tests/test_api.py

# Test with coverage
python -m pytest --cov=backend tests/
```

## Monitoring & Logs

### Health Checks
```bash
# Check all services
curl http://localhost:8000/health      # Backend API
curl http://localhost:11434/api/tags   # Ollama models
curl http://localhost:8501             # Frontend

# Docker container status
docker ps
docker stats
```

### Log Monitoring
```bash
# View application logs
docker logs agentic-backend-main -f
docker logs agentic-ollama-main -f
docker logs agentic-frontend-client-1 -f

# Local development logs
tail -f logs/app.log
tail -f logs/errors.log
```

### Performance Monitoring
```bash
# GPU usage (if available)
nvidia-smi -l 1

# Memory usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Network activity
netstat -i
```

## Troubleshooting

### Common Issues

**❌ GPU Required Error**
```bash
# The main server requires NVIDIA GPU
# Check GPU availability
nvidia-smi

# Install NVIDIA Docker runtime if needed
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

**❌ "Ollama not found" or Connection Refused**
```bash
# Restart Docker services
sudo docker restart agentic-ollama-main

# Check container logs
sudo docker logs agentic-ollama-main

# Manual Ollama installation (for local development)
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
```

**❌ Port Already in Use**
```bash
# Find what's using the port
sudo lsof -i :8502
sudo netstat -tulpn | grep :8000

# Kill conflicting processes
sudo kill -9 <PID>

# Or deploy client on different port
sudo ./deploy.sh client 5  # Uses ports 8505/8005
```

**❌ Multi-Client Session Issues**
```bash
# Check session management endpoints
curl http://localhost:8000/sessions

# Clear all sessions
curl -X DELETE http://localhost:8000/sessions

# Check client proxy health
curl http://localhost:8002/health  # Client 2
curl http://localhost:8003/health  # Client 3
```

**❌ Columns Layout Error (Fixed)**
```bash
# This was a Streamlit sidebar columns issue - now resolved
# If you see this error, make sure you have the latest code:
git pull origin main
sudo ./deploy.sh client 2  # Rebuild client
```

**❌ GPU Not Detected or Out of Memory**
```bash
# Check GPU status
nvidia-smi

# Use smaller model
docker exec agentic-ollama-main ollama pull llama3.2:1b

# Reduce token limit in config/app_config.py
LLM_CONFIG["max_tokens"] = 500

# Clear GPU memory
sudo pkill -f ollama
sudo docker restart agentic-ollama-main
```

**❌ Model Download Fails**
```bash
# Manual model pull with sudo
sudo docker exec -it agentic-ollama-main ollama pull mistral:7b

# Check available space
df -h

# Alternative model sources
sudo docker exec agentic-ollama-main ollama pull llama3.2:1b  # Smaller alternative
```

**❌ Frontend Won't Load**
```bash
# Check Streamlit status
sudo docker logs agentic-frontend-client-2

# Restart frontend
sudo docker restart agentic-frontend-client-2

# Check browser console for errors
# Try incognito mode (clear cache)
```

**❌ File Upload Issues**
```bash
# Check permissions
ls -la data/uploads/
sudo chmod 755 data/uploads/

# Check disk space
du -sh data/
df -h

# Clear upload cache
sudo rm -rf data/uploads/*.tmp
```

### Getting Help

- 📖 **Read the Guides**: Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) and [MULTI_CLIENT_USAGE_GUIDE.md](MULTI_CLIENT_USAGE_GUIDE.md)
- 🐛 **Check Logs**: Use `sudo docker logs <container-name>` to investigate issues  
- 💬 **Report Issues**: Open an issue with:
  - Error message and logs
  - System info (`python --version`, `docker --version`, `nvidia-smi`)
  - Steps to reproduce the problem
- 🔍 **Health Check**: Run `curl http://localhost:8000/health` to verify system status

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)**: 1-minute deployment guide
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**: Complete deployment instructions
- **[MULTI_CLIENT_USAGE_GUIDE.md](MULTI_CLIENT_USAGE_GUIDE.md)**: Multi-client setup and usage
- **[MULTI_CLIENT_SESSION_SUMMARY.md](MULTI_CLIENT_SESSION_SUMMARY.md)**: Implementation details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request with detailed description

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🎯 Ready to get started?** Run `sudo ./deploy.sh main` to deploy the main server and `sudo ./deploy.sh client 2` for your first client instance!
df -h

# Alternative model sources
ollama pull llama3.2:1b  # Smaller alternative
```

**❌ Frontend Won't Load**
```bash
# Check Streamlit status
docker logs agentic-frontend-client-1

# Restart frontend
docker restart agentic-frontend-client-1

# Check browser console for errors
# Try incognito mode (clear cache)
```

**❌ File Upload Issues**
```bash
# Check permissions
ls -la data/uploads/
chmod 755 data/uploads/

# Check disk space
du -sh data/
df -h

# Clear upload cache
rm -rf data/uploads/*.tmp
```

### Getting Help
- 📖 Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed setup
- 🐛 Check logs: `docker logs <container-name>`
- 💬 Open an issue with:
  - Error message
  - System info (`python --version`, `docker --version`)
  - Steps to reproduce

## 🤝 Contributing

### Ways to Contribute
- 🐛 **Bug Reports**: Found an issue? Open a detailed bug report
- 💡 **Feature Requests**: Have an idea? Suggest new features
- 📝 **Documentation**: Improve docs, add examples
- 🧪 **Testing**: Add tests, improve coverage
- 🛠️ **Code**: Fix bugs, implement features

### Development Process
1. **Fork** the repository
2. **Create** a feature branch:
   ```bash
   git checkout -b feature/awesome-new-feature
   ```
3. **Develop** with tests:
   ```bash
   # Make your changes
   # Add tests in tests/
   python -m pytest tests/
   ```
4. **Document** your changes:
   ```bash
   # Update docstrings
   # Update README if needed
   # Add example usage
   ```
5. **Submit** a pull request:
   - Clear description of changes
   - Link to any related issues
   - Include screenshots if UI changes

### Code Style
```bash
# Format code
black backend/ frontend/
isort backend/ frontend/

# Lint code  
flake8 backend/ frontend/
mypy backend/

# Run pre-commit hooks
pre-commit run --all-files
```

## 📚 Additional Resources

- 📖 **[Deployment Guide](DEPLOYMENT_GUIDE.md)**: Detailed deployment instructions
- 🔧 **[API Documentation](http://localhost:8000/docs)**: Interactive API docs (when server is running)
- 🤖 **[Ollama Models](https://ollama.ai/library)**: Browse available models
- 🐳 **[Docker Hub](https://hub.docker.com/r/ollama/ollama)**: Ollama Docker images

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ using Python, Docker, and AI**

[⭐ Star this repo](../../stargazers) • [🐛 Report Bug](../../issues) • [💡 Request Feature](../../issues)

</div>
# Agentic AI Project

A sophisticated multi-agent AI system for code generation and document analysis using local language models with GPU acceleration support.

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Features

### Core Capabilities
- **Code Agent**: Generates, analyzes, and executes Python, C, and C++ code with intelligent error handling
- **Document Agent**: Advanced analysis of PDF, Excel, Word, and text files with RAG capabilities
- **Smart Routing**: Automatically routes queries to the most appropriate agent based on context
- **Multi-Modal Support**: Handle both text and file inputs seamlessly

### Technical Features
- **Local LLM Support**: Ollama integration (Mistral 7B, LLaMA 3.2, CodeLlama)
- **GPU Acceleration**: NVIDIA GPU support for faster inference
- **Scalable Architecture**: Client-server deployment with multiple frontend instances
- **RESTful API**: FastAPI backend for integration with external systems
- **Modern UI**: Streamlit-based interface with file upload and chat capabilities

### Deployment Options
- **Local Development**: Single-command setup for development
- **Docker Deployment**: Production-ready containerized deployment
- **Client-Server Architecture**: Scale with multiple client instances
- **GPU Support**: Automatic GPU detection and utilization

## 🏃 Quick Start

### Option 1: Local Development
Perfect for development and testing:

```bash
# Clone the repository
git clone <repository-url>
cd Agentic-AI-Project-BDL

# Automated setup (installs dependencies and starts Ollama)
python setup-dev.py

# Launch the application
python main.py
```

### Option 2: Docker Deployment
Recommended for production and easy scaling:

```bash
# Clone and navigate
git clone <repository-url>
cd Agentic-AI-Project-BDL

# Make deployment script executable
chmod +x deploy.sh

# Deploy main server with GPU support
./deploy.sh main

# (Optional) Deploy additional client instances
./deploy.sh client 1
./deploy.sh client 2
```

**Access Points:**
- **Web Interface**: `http://localhost:8501`
- **API Documentation**: `http://localhost:8000/docs`
- **Ollama API**: `http://localhost:11434`

### Option 3: API-Only Mode
For integration with existing applications:

```bash
# Start only the backend API
uvicorn backend.api_server:app --host 0.0.0.0 --port 8000

# Test the API
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Generate a Python function to calculate fibonacci numbers"}'
```

## 📋 Requirements

### System Requirements
- **Python**: 3.12+ (for local development)
- **Memory**: 8GB+ RAM (16GB recommended for optimal performance)
- **Storage**: ~10GB free space (for models and containers)
- **OS**: Linux, macOS, or Windows with WSL2

### Optional but Recommended
- **Docker & Docker Compose**: For containerized deployment
- **NVIDIA GPU**: GTX 1060+ or RTX series for GPU acceleration
- **CUDA**: Version 11.0+ (automatically handled in Docker)

### Quick System Check
```bash
# Verify Python version
python --version

# Check available memory
free -h  # Linux/macOS
wmic computersystem get TotalPhysicalMemory  # Windows

# Verify GPU (if available)
nvidia-smi

# Check Docker installation
docker --version && docker compose version
```

## 🏗️ Architecture

### System Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   LLM Provider  │
│  (Streamlit)    │ ◄──► │   (FastAPI)     │ ◄──► │   (Ollama)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Chat Interface  │    │ Agent Router    │    │ GPU Acceleration│
│ File Uploader   │    │ Code Agent      │    │ Model Storage   │
│ Response Stream │    │ Document Agent  │    │ API Endpoints   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Agent System
- **Agent Router**: Intelligently routes queries based on content analysis
- **Code Agent**: Specializes in code generation, analysis, and execution
- **Document Agent**: Handles file processing, summarization, and Q&A
- **Tool Integration**: Extensible tool system for specialized tasks

### Deployment Modes
1. **Standalone**: All components on a single machine
2. **Client-Server**: Centralized backend with multiple client frontends
3. **API-Only**: Backend service for external integration

## 📁 Project Structure

```
Agentic-AI-Project-BDL/
├── 🚀 main.py                    # Local application entry point
├── ⚙️ setup-dev.py               # Development setup script  
├── 🐳 deploy.sh                  # Docker deployment script
├── 📖 DEPLOYMENT_GUIDE.md        # Detailed deployment instructions
├── 🔧 backend/
│   ├── 🤖 agents/               # AI agent implementations
│   │   ├── base_agent.py        # Base agent class
│   │   ├── code_agent.py        # Code generation & analysis
│   │   └── doc_agent.py         # Document processing
│   ├── 🛠️ tools/                # Specialized tools
│   │   ├── code_tools/          # Code execution & analysis
│   │   └── doc_tools/           # Document processing tools
│   ├── 🧠 llm_providers/        # LLM integrations
│   │   ├── ollama_provider.py   # Ollama integration
│   │   └── tensorrt_provider.py # TensorRT-LLM support
│   ├── 🎭 graphs/               # Workflow orchestration
│   │   └── agent_controller.py  # LangGraph controller
│   ├── 🔗 utils/                # Utilities
│   │   ├── memory.py            # Memory management
│   │   └── router.py            # Request routing
│   └── 🌐 api_server.py         # FastAPI backend server
├── 🎨 frontend/
│   ├── app.py                   # Standalone Streamlit app
│   ├── client_app.py            # Client-server frontend
│   └── components/              # Reusable UI components
├── ⚙️ config/                   # Configuration files
│   ├── app_config.py            # Main application config
│   └── llm_config.py            # LLM-specific settings
├── 🐳 deployment/               # Docker configurations
│   ├── docker-compose.*.yml     # Various deployment configs
│   ├── Dockerfile.*             # Service-specific Dockerfiles
│   └── scripts/                 # Deployment scripts
└── 📊 data/                     # Data storage
    └── uploads/                 # User uploaded files
```

### Key Components
- **Agent System**: Modular AI agents with specialized capabilities
- **Tool Integration**: Extensible tool system for code execution and document processing  
- **LLM Providers**: Support for multiple language model backends
- **Workflow Engine**: LangGraph-based orchestration for complex tasks
- **API Layer**: RESTful API for external integrations

## ⚙️ Configuration & Customization

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

## 💡 Usage Examples

### Code Generation
```
User: "Create a Python function to analyze sentiment of text using transformers"

AI Response:
✅ Code generated and tested
✅ Dependencies identified  
✅ Example usage provided
✅ Error handling included
```

### Document Analysis
```
Upload: business_report.pdf (2.3MB)
Query: "What are the key financial metrics mentioned?"

AI Response:
📊 Revenue: $2.4M (↑15% YoY)
📈 Profit Margin: 18.5%
💰 Cash Flow: $450K positive
📋 Full summary with page references
```

### Multi-Agent Workflow
```
Query: "Analyze this CSV file and create a visualization script"

Process:
1. 📄 Document Agent: Parses CSV structure  
2. 🔄 Router: Determines need for both agents
3. 💻 Code Agent: Generates matplotlib script
4. 🎯 Result: Working visualization code + data insights
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

## 🛠️ Development Workflow

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

## 📊 Monitoring & Logs

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

## 🔧 Troubleshooting

### Common Issues

**❌ "Ollama not found" or Connection Refused**
```bash
# Install Ollama (if not using Docker)
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve

# Or restart Docker services
docker restart agentic-ollama-main
```

**❌ Port Already in Use**
```bash
# Find what's using the port
sudo lsof -i :8501
sudo netstat -tulpn | grep :8000

# Use different ports
export STREAMLIT_PORT=8502
export API_PORT=8002

# Or kill the process
sudo kill -9 <PID>
```

**❌ GPU Not Detected or Out of Memory**
```bash
# Check GPU status
nvidia-smi

# Use smaller model
ollama pull llama3.2:1b

# Reduce token limit in config/app_config.py
LLM_CONFIG["max_tokens"] = 500

# Clear GPU memory
sudo pkill -f ollama
docker restart agentic-ollama-main
```

**❌ Model Download Fails**
```bash
# Manual model pull
docker exec -it agentic-ollama-main ollama pull mistral:7b

# Check available space
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
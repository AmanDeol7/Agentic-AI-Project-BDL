# Multi-Client Session Management Usage Guide

## 🌟 Overview

The Agentic AI project now supports multiple simultaneous clients with complete session isolation. Each client can have independent conversations, file uploads, and AI assistant instances without interfering with others.

## 🚀 Quick Start

### 1. Deploy the System

#### Deploy Main Server (GPU Required)
```bash
sudo ./deploy.sh main
```

#### Deploy Client Instances
```bash
# Deploy multiple clients
sudo ./deploy.sh client 2
sudo ./deploy.sh client 3
sudo ./deploy.sh client 4
# ... add as many clients as needed
```

### 2. Access Your Clients

| Client | Frontend URL | Backend Proxy URL | Description |
|--------|--------------|-------------------|-------------|
| Client 2 | http://localhost:8502 | http://localhost:8002 | First client instance |
| Client 3 | http://localhost:8503 | http://localhost:8003 | Second client instance |
| Client 4 | http://localhost:8504 | http://localhost:8004 | Third client instance |
| Client N | http://localhost:850(N) | http://localhost:800(N) | Nth client instance |

### 3. Main Server Access
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 💡 Key Features

### Session Management
Each client automatically gets a unique session when they first connect:

1. **Automatic Session Creation**: Sessions are created automatically on first interaction
2. **Session Persistence**: Sessions persist for 60 minutes of inactivity
3. **Session Isolation**: Complete isolation between different client sessions
4. **Session Management UI**: Built-in interface for session control

### Client Features
- ✅ **Independent Conversations**: Each client has separate chat history
- ✅ **Isolated File Uploads**: Files are stored in session-specific directories
- ✅ **Private Assistant Instances**: Each session gets its own AI assistant
- ✅ **Session Context Management**: Clear, delete, or manage session context
- ✅ **Real-time Session Statistics**: Monitor session health and usage

## 🎯 Use Cases

### 1. Multi-User Development Team
```
Team Lead (Client 2):     http://localhost:8502
Frontend Dev (Client 3):  http://localhost:8503
Backend Dev (Client 4):   http://localhost:8504
QA Engineer (Client 5):   http://localhost:8505
```

### 2. Different Project Contexts
```
Project A (Client 2): Working on microservices
Project B (Client 3): Working on frontend React app
Project C (Client 4): Working on data analysis
```

### 3. Training and Demos
```
Trainer (Client 2):    Demonstrating features
Student 1 (Client 3):  Following along
Student 2 (Client 4):  Practicing independently
```

## 🛠️ Session Management

### Frontend Session Controls

Each client frontend includes a session management sidebar with:

#### Session Information
- Current session ID (truncated for display)
- Client ID
- Session creation time
- Last activity timestamp

#### Session Actions
- **📊 Session Details**: View complete session information
- **🧹 Clear Session**: Clear conversation history while keeping the session
- **🗑️ Delete Session**: Completely remove the session and all data
- **🔗 Create New Session**: Start a fresh session
- **📋 List All Sessions**: View all active sessions (admin view)

### API Session Management

You can also manage sessions programmatically:

#### Create a Session
```bash
curl -X POST http://localhost:8002/sessions \
  -H "Content-Type: application/json" \
  -d '{"client_id": "my_client"}'
```

#### Get Session Info
```bash
curl http://localhost:8002/sessions/{session_id} \
  -H "x-session-id: {session_id}"
```

#### List All Sessions
```bash
curl http://localhost:8000/sessions
```

#### Clear Session Context
```bash
curl -X POST http://localhost:8002/sessions/{session_id}/clear \
  -H "x-session-id: {session_id}"
```

#### Delete Session
```bash
curl -X DELETE http://localhost:8002/sessions/{session_id} \
  -H "x-session-id: {session_id}"
```

## 📁 File Upload Isolation

Files uploaded by different clients are automatically isolated:

```
data/uploads/
├── session_abc123-def4-5678-9012-345678901234/
│   ├── document1.pdf
│   └── spreadsheet1.xlsx
├── session_xyz789-abc1-2345-6789-012345678901/
│   ├── code_file.py
│   └── requirements.txt
└── session_def456-ghi7-8901-2345-678901234567/
    └── presentation.pptx
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_URL` | `http://localhost:8000` | Main server URL |
| `SESSION_TIMEOUT` | `60` | Session timeout in minutes |
| `CLIENT_ID` | Auto-generated | Unique client identifier |

### Docker Environment

Each client runs in isolated Docker containers:
- **Frontend Container**: Runs Streamlit application
- **Backend Proxy**: Forwards requests to main server with session headers
- **Main Server**: Handles all AI processing and session management

## 🔍 Monitoring and Debugging

### Check Container Status
```bash
sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### View Logs
```bash
# Main server logs
sudo docker compose -f deployment/docker-compose.main-server-gpu.yml logs -f

# Client 2 logs
sudo docker compose -p agentic-client-2 -f deployment/docker-compose.client-server.yml logs -f

# Client 3 logs
sudo docker compose -p agentic-client-3 -f deployment/docker-compose.client-server.yml logs -f
```

### Health Checks
```bash
# Main server health
curl http://localhost:8000/health

# Client proxy health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

### Session Statistics
```bash
# Get session statistics
curl http://localhost:8000/sessions | jq '.stats'
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
sudo netstat -tulpn | grep :8502

# Kill the process or use different client ID
sudo ./deploy.sh client 10  # Uses ports 8510/8010
```

#### 2. Client Can't Connect
```bash
# Verify main server is running
curl http://localhost:8000/health

# Check client proxy logs
sudo docker logs agentic-backend-proxy-2
```

#### 3. Sessions Not Isolated
```bash
# Verify unique session IDs
curl http://localhost:8002/sessions -s | jq '.session_id'
curl http://localhost:8003/sessions -s | jq '.session_id'
```

#### 4. Memory Issues
```bash
# Check container resource usage
sudo docker stats

# Clean up old sessions if needed
curl -X DELETE http://localhost:8000/sessions/{old_session_id}
```

### Reset Everything
```bash
# Stop all clients
sudo docker compose -p agentic-client-2 -f deployment/docker-compose.client-server.yml down
sudo docker compose -p agentic-client-3 -f deployment/docker-compose.client-server.yml down

# Stop main server
sudo docker compose -f deployment/docker-compose.main-server-gpu.yml down

# Redeploy
sudo ./deploy.sh main
sudo ./deploy.sh client 2
sudo ./deploy.sh client 3
```

## 🧪 Testing Session Isolation

Run the built-in test to verify session isolation:

```bash
python test_multi_client_sessions.py
```

This test verifies:
- ✅ Multiple clients can create unique sessions
- ✅ Sessions are properly isolated
- ✅ Session management works across clients
- ✅ Conversation history is separate between sessions

## 📈 Performance Considerations

### Scaling Guidelines
- **Small Team (2-5 users)**: Deploy 2-5 client instances
- **Medium Team (5-15 users)**: Deploy 5-15 client instances
- **Large Team (15+ users)**: Consider load balancing and multiple main servers

### Resource Requirements
- **Main Server**: 4GB+ RAM, GPU recommended
- **Client Instance**: 512MB RAM per client
- **Session Storage**: ~10MB per active session

### Session Cleanup
- Sessions auto-expire after 60 minutes of inactivity
- Expired sessions are automatically cleaned up
- Manual cleanup available through session management interface

---

## 🎉 Conclusion

The multi-client session management system provides a robust, scalable solution for teams and organizations needing isolated AI assistant instances. Each client gets their own private workspace while sharing the powerful backend infrastructure.

For additional support or advanced configuration, refer to the main README.md and deployment documentation.

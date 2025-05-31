#!/bin/bash
"""
Configure Ollama for CPU-only operation to avoid CUDA memory issues.
"""

echo "🔧 Configuring Ollama for CPU-only operation..."

# Stop any running Ollama processes
echo "Stopping Ollama service..."
ollama stop deepseek-r1:8b 2>/dev/null || true
ollama stop mistral:latest 2>/dev/null || true

# Set environment variables for CPU-only operation
export CUDA_VISIBLE_DEVICES=""
export OLLAMA_GPU_LAYERS=0
export OLLAMA_NUM_GPU=0

echo "✅ Environment configured for CPU-only mode"

# Test that mistral model is available
echo "📋 Checking available models..."
ollama list

# Pull mistral if not available
if ! ollama list | grep -q "mistral:latest"; then
    echo "📥 Pulling mistral model..."
    ollama pull mistral
fi

echo "✅ Ollama configured for CPU-only operation"
echo "   - CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"
echo "   - OLLAMA_GPU_LAYERS=$OLLAMA_GPU_LAYERS"
echo "   - OLLAMA_NUM_GPU=$OLLAMA_NUM_GPU"

# Test the configuration
echo "🧪 Testing Ollama with simple prompt..."
echo "What is 2+2?" | ollama run mistral --verbose

echo "🎉 Configuration complete! You can now run the Streamlit app."

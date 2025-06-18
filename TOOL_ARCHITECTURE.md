# Tool Architecture Documentation

## Overview
The Agentic AI Project uses a streamlined tool architecture with two specialized tools that handle all core functionality.

## Active Tools

### 1. Code Executor (`backend/tools/code_tools/executor.py`)

**Purpose**: Safe execution of code in multiple programming languages

**Features**:
- ✅ **Multi-language support**: Python, C, C++
- ✅ **Security**: Sandboxed execution with timeout protection
- ✅ **Compilation**: Automatic compilation for C/C++ with proper compiler flags
- ✅ **Error handling**: Comprehensive error reporting for both compilation and runtime errors
- ✅ **Cleanup**: Automatic temporary file cleanup

**Usage**:
```python
executor = CodeExecutor(timeout=15)
result = executor.run({
    "code": "print('Hello, World!')",
    "language": "python"
})
```

**Integration**: Used by `CodeAgent` for all code-related tasks

### 2. Document Processor (`backend/tools/doc_tools/document_processor.py`)

**Purpose**: Unified document processing with AI-powered analysis

**Features**:
- ✅ **Multi-format support**: PDF, Word (.docx), Excel (.xlsx), CSV, Text, Markdown
- ✅ **AI-powered analysis**: TensorRT-LLM integration with Ollama fallback
- ✅ **Multiple operations**: Extract, analyze, summarize, question-answering
- ✅ **Content awareness**: Intelligent content parsing and structuring

**Operations**:
- `extract`: Raw content extraction
- `summarize`: AI-powered summarization
- `analyze`: Deep document analysis (topics, entities, sentiment)
- `question_answer`: Context-aware Q&A
- `process`: General document processing

**Usage**:
```python
processor = DocumentProcessor(upload_dir=Path("uploads"), llm_provider=llm)
result = processor.run({
    "action": "summarize",
    "file_path": "document.pdf"
})
```

**Integration**: Used by `DocAgent` for all document-related tasks

## Architecture Benefits

### 🎯 **Simplified Design**
- Two specialized tools instead of multiple overlapping ones
- Clear separation of concerns
- Reduced complexity and maintenance overhead

### 🚀 **Performance**
- Unified processing pipelines
- Shared LLM provider instances
- Optimized resource usage

### 🔧 **Maintainability**
- Single source of truth for each domain
- Consistent error handling patterns
- Simplified testing and debugging

## Tool Integration Flow

```
User Query → Agent Router → Appropriate Agent → Tool Execution → Response
```

### Code Flow
```
Code Query → CodeAgent → CodeExecutor → [Language Handler] → Result
```

### Document Flow
```
Document Query → DocAgent → DocumentProcessor → [Format Handler] → [LLM Analysis] → Result
```

## Extension Guidelines

### Adding New Code Language Support
1. Add language handler method to `CodeExecutor._execute_*()` pattern
2. Update language detection in `CodeExecutor.run()`
3. Add appropriate compiler/interpreter logic
4. Test with sample code

### Adding New Document Format Support
1. Add format handler method to `DocumentProcessor._process_*()` pattern
2. Update format detection in file extension mapping
3. Implement content extraction logic
4. Test with sample documents

### Best Practices
- Maintain unified error handling patterns
- Use consistent return formats
- Include proper cleanup mechanisms
- Add comprehensive logging
- Write unit tests for new features

## Removed Tools (Reference)

The following tools were removed during cleanup as they provided duplicate functionality:

- `document_analyzer.py` → Integrated into `document_processor.py`
- `document_extractor.py` → Integrated into `document_processor.py`
- `document_summarizer.py` → Integrated into `document_processor.py`
- `excel_loader.py` → Integrated into `document_processor.py`
- `pdf_loader.py` → Integrated into `document_processor.py`
- `rag_processor.py` → Replaced by `document_processor.py`

This consolidation provides better maintainability while preserving all functionality.

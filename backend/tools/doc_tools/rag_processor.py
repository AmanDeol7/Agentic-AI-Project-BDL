from typing import Dict, Any, List, Optional
import os
from pathlib import Path
import threading
from ...rag.vector_store import VectorStore, _configure_torch
from ...rag.retriever import RAGRetriever
from .pdf_loader import PDFLoader

# Global lock for processor initialization
_processor_lock = threading.Lock()

class RAGDocumentProcessor:
    """
    RAG-based document processor that can ingest and query documents.
    """
    
    name = "rag_processor"
    description = "Processes documents using RAG for accurate question answering"
    
    def __init__(self, upload_dir: Optional[Path] = None):
        """
        Initialize the RAG processor.
        
        Args:
            upload_dir: Directory where uploaded files are stored
        """
        self.upload_dir = upload_dir
        self._vector_store = None
        self._retriever = None
        self._initialized = False
        self.pdf_loader = PDFLoader(upload_dir)
    
    def _ensure_initialized(self):
        """Ensure the processor is properly initialized."""
        if not self._initialized:
            with _processor_lock:
                if not self._initialized:
                    # Configure PyTorch before any initialization
                    _configure_torch()
                    self._initialized = True
    
    @property
    def vector_store(self) -> VectorStore:
        """Lazy load the vector store."""
        self._ensure_initialized()
        if self._vector_store is None:
            with _processor_lock:
                if self._vector_store is None:
                    self._vector_store = VectorStore()
        return self._vector_store
    
    @property
    def retriever(self) -> RAGRetriever:
        """Lazy load the retriever."""
        self._ensure_initialized()
        if self._retriever is None:
            with _processor_lock:
                if self._retriever is None:
                    self._retriever = RAGRetriever(self.vector_store)
        return self._retriever
    
    def run(self, args: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
        """
        Run the RAG processor tool.
        
        Args:
            args: Arguments for the tool
            context: Optional context for the tool execution
            
        Returns:
            Dictionary with processing results
        """
        try:
            self._ensure_initialized()
            action = args.get('action', 'query')
            
            if action == 'ingest':
                return self._ingest_document(args)
            elif action == 'query':
                return self._query_documents(args)
            elif action == 'stats':
                return self._get_stats()
            elif action == 'delete':
                return self._delete_document(args)
            else:
                return {'error': f'Unknown action: {action}'}
        except Exception as e:
            error_msg = str(e)
            print(f"RAG processor error: {error_msg}")
            return {
                'error': f'RAG processor error: {error_msg}',
                'success': False,
                'details': 'The document processor encountered an error. Please try again or check the file format.'
            }
    
    def _ingest_document(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ingest a document into the vector store.
        
        Args:
            args: Arguments containing file path and metadata
            
        Returns:
            Ingestion results
        """
        file_path = args.get('file_path') or args.get('file')
        
        if not file_path:
            return {'error': 'No file path provided'}
        
        # If a relative path is provided and upload_dir is set, combine them
        if self.upload_dir and not os.path.isabs(file_path):
            file_path = self.upload_dir / file_path
        
        if not os.path.exists(file_path):
            return {'error': f'File not found: {file_path}'}
        
        try:
            # Extract content based on file type
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.pdf':
                # Use PDF loader to extract text
                pdf_result = self.pdf_loader.run({'file': file_path})
                if 'error' in pdf_result:
                    return pdf_result
                
                # Combine all pages
                if isinstance(pdf_result['text'], list):
                    content = '\n\n'.join(pdf_result['text'])
                else:
                    content = pdf_result['text']
                
                metadata = {
                    'file_type': 'pdf',
                    'num_pages': pdf_result.get('num_pages', 1)
                }
                
            elif file_ext in ['.txt', '.py', '.js', '.c', '.cpp', '.java']:
                # Read text files directly
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                metadata = {
                    'file_type': file_ext[1:]  # Remove the dot
                }
            
            else:
                return {'error': f'Unsupported file type: {file_ext}'}
            
            # Add to vector store
            added = self.vector_store.add_document(
                file_path=str(file_path),
                content=content,
                metadata=metadata
            )
            
            if added:
                stats = self.vector_store.get_document_stats()
                return {
                    'success': True,
                    'message': f'Document ingested successfully',
                    'file_path': str(file_path),
                    'content_length': len(content),
                    'stats': stats
                }
            else:
                return {
                    'success': True,
                    'message': 'Document already exists in vector store',
                    'file_path': str(file_path)
                }
                
        except Exception as e:
            return {'error': f'Failed to ingest document: {str(e)}'}
    
    def _query_documents(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query the document collection.
        
        Args:
            args: Arguments containing query
            
        Returns:
            Query results
        """
        query = args.get('query')
        if not query:
            return {'error': 'No query provided', 'success': False}
        
        try:
            # Retrieve relevant context
            retrieval_result = self.retriever.retrieve_context(
                query=query,
                max_chunks=args.get('max_chunks', 5),
                max_context_length=args.get('max_context_length', 2000)
            )
            
            if not retrieval_result.get('context'):
                return {
                    'success': True,
                    'query': query,
                    'context': '',
                    'sources': [],
                    'num_chunks': 0,
                    'message': 'No relevant context found for the query.'
                }
            
            # Format RAG prompt
            rag_prompt = self.retriever.format_rag_prompt(
                query=query,
                context=retrieval_result['context']
            )
            
            return {
                'success': True,
                'query': query,
                'context': retrieval_result['context'],
                'sources': retrieval_result['sources'],
                'num_chunks': retrieval_result['num_chunks'],
                'rag_prompt': rag_prompt,
                'context_length': retrieval_result['total_context_length']
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"Query error: {error_msg}")
            return {
                'error': f'Failed to query documents: {error_msg}',
                'success': False,
                'details': 'An error occurred while processing your query. Please try again.'
            }
    
    def _get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        try:
            stats = self.vector_store.get_document_stats()
            return {
                'success': True,
                'stats': stats
            }
        except Exception as e:
            return {'error': f'Failed to get stats: {str(e)}'}

    def _delete_document(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete a document from the vector store and optionally from disk.
        
        Args:
            args: Arguments containing file path and delete_from_disk flag
            
        Returns:
            Deletion results
        """
        file_path = args.get('file_path') or args.get('file')
        delete_from_disk = args.get('delete_from_disk', False)
        
        if not file_path:
            return {'error': 'No file path provided'}
        
        # If a relative path is provided and upload_dir is set, combine them
        if self.upload_dir and not os.path.isabs(file_path):
            file_path = self.upload_dir / file_path
        
        try:
            # Delete from vector store
            deleted = self.vector_store.delete_document(str(file_path))
            
            if not deleted:
                return {
                    'success': False,
                    'error': f'Document {file_path} not found in vector store'
                }
            
            # Optionally delete from disk
            if delete_from_disk and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    disk_deleted = True
                except Exception as e:
                    print(f"Error deleting file from disk: {e}")
                    disk_deleted = False
            else:
                disk_deleted = False
            
            # Get updated stats
            stats = self.vector_store.get_document_stats()
            
            return {
                'success': True,
                'message': 'Document deleted successfully',
                'file_path': str(file_path),
                'deleted_from_disk': disk_deleted,
                'stats': stats
            }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to delete document: {str(e)}'
            }

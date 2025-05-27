import numpy as np
import faiss
import pickle
import os
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import hashlib
import json
import warnings
import threading

# Global lock for model initialization
_model_lock = threading.Lock()
_initialized = False

def _configure_torch():
    """Configure PyTorch for optimal performance and stability."""
    global _initialized
    if not _initialized:
        with _model_lock:
            if not _initialized:
                try:
                    import torch
                    
                    # Disable tokenizer parallelism
                    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
                    
                    # Suppress specific warnings
                    warnings.filterwarnings('ignore', category=UserWarning, module='torch')
                    warnings.filterwarnings('ignore', category=UserWarning, module='transformers')
                    
                    # Set PyTorch to use CPU by default to avoid CUDA issues
                    if not torch.cuda.is_available():
                        os.environ['CUDA_VISIBLE_DEVICES'] = ''
                    
                    # Disable PyTorch's file watcher
                    if hasattr(torch.utils.data._utils.worker, '_worker_loop'):
                        torch.utils.data._utils.worker._worker_loop = lambda *args, **kwargs: None
                    
                    _initialized = True
                except ImportError:
                    print("PyTorch not available, continuing without GPU support")
                    _initialized = True

class VectorStore:
    """
    Offline vector store using FAISS for similarity search.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", store_dir: str = "./data/vector_store"):
        """
        Initialize the vector store.
        
        Args:
            model_name: Name of the sentence transformer model
            store_dir: Directory to store vector indices and metadata
        """
        self.model_name = model_name
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize variables
        self.encoder = None
        self.embedding_dim = None
        self.index = None
        self.documents = []
        self.metadata = []
        
        # Configure PyTorch before any model loading
        _configure_torch()
        
        # Load existing index if available
        self._load_index()
    
    def _ensure_encoder(self):
        """Lazy load the encoder model with proper initialization."""
        if self.encoder is None:
            with _model_lock:
                if self.encoder is None:
                    try:
                        # Import here to avoid circular imports and control initialization
                        from sentence_transformers import SentenceTransformer
                        import torch
                        
                        print(f"Loading embedding model: {self.model_name}")
                        # Configure model to use CPU if CUDA is not available
                        device = 'cpu' if not torch.cuda.is_available() else 'cuda'
                        self.encoder = SentenceTransformer(self.model_name, device=device)
                        self.embedding_dim = self.encoder.get_sentence_embedding_dimension()
                        
                        # Initialize FAISS index if not already done
                        if self.index is None:
                            self.index = faiss.IndexFlatIP(self.embedding_dim)
                    except Exception as e:
                        print(f"Error initializing encoder: {e}")
                        raise
    
    def _get_file_hash(self, file_path: str) -> str:
        """Get hash of file for caching."""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _load_index(self):
        """Load existing FAISS index and metadata."""
        index_path = self.store_dir / "index.faiss"
        metadata_path = self.store_dir / "metadata.pkl"
        documents_path = self.store_dir / "documents.pkl"
        
        if index_path.exists() and metadata_path.exists() and documents_path.exists():
            try:
                # Load FAISS index
                self.index = faiss.read_index(str(index_path))
                
                # Load metadata
                with open(metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                
                # Load documents
                with open(documents_path, 'rb') as f:
                    self.documents = pickle.load(f)
                
                print(f"Loaded existing vector store with {len(self.documents)} chunks")
            except Exception as e:
                print(f"Error loading existing index: {e}")
                self._reset_index()
        else:
            print("No existing vector store found, starting fresh")
            self._reset_index()
    
    def _save_index(self):
        """Save FAISS index and metadata."""
        index_path = self.store_dir / "index.faiss"
        metadata_path = self.store_dir / "metadata.pkl"
        documents_path = self.store_dir / "documents.pkl"
        
        try:
            # Save FAISS index
            faiss.write_index(self.index, str(index_path))
            
            # Save metadata
            with open(metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            # Save documents
            with open(documents_path, 'wb') as f:
                pickle.dump(self.documents, f)
            
            print("Vector store saved successfully")
        except Exception as e:
            print(f"Error saving vector store: {e}")
    
    def _reset_index(self):
        """Reset the index and metadata."""
        self.documents = []
        self.metadata = []
        # Don't create index here, wait for encoder initialization
    
    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings near the chunk boundary
                sentence_end = max(
                    text.rfind('.', start, end),
                    text.rfind('!', start, end),
                    text.rfind('?', start, end)
                )
                
                if sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            
            if start >= len(text):
                break
        
        return chunks
    
    def add_document(self, file_path: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Add a document to the vector store.
        
        Args:
            file_path: Path to the document file
            content: Text content of the document
            metadata: Additional metadata for the document
            
        Returns:
            True if document was added, False if already exists
        """
        # Ensure encoder is loaded
        self._ensure_encoder()
        
        # Check if document already exists
        file_hash = self._get_file_hash(file_path)
        
        # Check if this file is already indexed
        for meta in self.metadata:
            if meta.get('file_hash') == file_hash:
                print(f"Document {file_path} already indexed")
                return False
        
        # Chunk the document
        chunks = self.chunk_text(content)
        print(f"Created {len(chunks)} chunks from {file_path}")
        
        # Generate embeddings for chunks
        embeddings = self.encoder.encode(chunks, show_progress_bar=True)
        
        # Normalize embeddings for cosine similarity
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Add to FAISS index
        self.index.add(embeddings.astype('float32'))
        
        # Store documents and metadata
        for i, chunk in enumerate(chunks):
            self.documents.append(chunk)
            chunk_metadata = {
                'file_path': file_path,
                'file_hash': file_hash,
                'chunk_id': len(self.documents) - 1,
                'chunk_index': i,
                'total_chunks': len(chunks),
                **(metadata or {})
            }
            self.metadata.append(chunk_metadata)
        
        # Save the updated index
        self._save_index()
        
        print(f"Added {len(chunks)} chunks from {file_path} to vector store")
        return True
    
    def search(self, query: str, k: int = 5, score_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            k: Number of results to return
            score_threshold: Minimum similarity score
            
        Returns:
            List of search results with scores and metadata
        """
        try:
            # Ensure encoder is loaded
            self._ensure_encoder()
            
            if len(self.documents) == 0:
                return []
            
            # Generate query embedding
            with torch.no_grad():  # Disable gradient computation
                query_embedding = self.encoder.encode([query], show_progress_bar=False)
                query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
            
            # Search in FAISS
            scores, indices = self.index.search(query_embedding.astype('float32'), min(k, len(self.documents)))
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if score >= score_threshold:
                    results.append({
                        'content': self.documents[idx],
                        'score': float(score),
                        'metadata': self.metadata[idx]
                    })
            
            return results
        except Exception as e:
            print(f"Error during search: {e}")
            return []
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        if not self.metadata:
            return {'total_chunks': 0, 'total_documents': 0}
        
        unique_files = set(meta['file_path'] for meta in self.metadata)
        
        return {
            'total_chunks': len(self.documents),
            'total_documents': len(unique_files),
            'embedding_dimension': self.embedding_dim,
            'model_name': self.model_name,
            'documents': list(unique_files)
        }

    def delete_document(self, file_path: str) -> bool:
        """
        Delete a document and all its chunks from the vector store.
        
        Args:
            file_path: Path to the document to delete
            
        Returns:
            True if document was deleted, False if not found
        """
        try:
            # Find all chunks belonging to this file
            chunks_to_remove = []
            for i, meta in enumerate(self.metadata):
                if meta['file_path'] == file_path:
                    chunks_to_remove.append(i)
            
            if not chunks_to_remove:
                print(f"Document {file_path} not found in vector store")
                return False
            
            # Remove chunks in reverse order to maintain correct indices
            for idx in sorted(chunks_to_remove, reverse=True):
                del self.documents[idx]
                del self.metadata[idx]
            
            # Rebuild the FAISS index
            if self.documents:
                # Ensure encoder is loaded
                self._ensure_encoder()
                
                # Generate new embeddings for remaining documents
                embeddings = self.encoder.encode(self.documents, show_progress_bar=True)
                embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
                
                # Create new index
                self.index = faiss.IndexFlatIP(self.embedding_dim)
                self.index.add(embeddings.astype('float32'))
            else:
                # If no documents left, reset the index
                self.index = None
                self._reset_index()
            
            # Save the updated index
            self._save_index()
            
            print(f"Deleted document {file_path} and its {len(chunks_to_remove)} chunks from vector store")
            return True
            
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False

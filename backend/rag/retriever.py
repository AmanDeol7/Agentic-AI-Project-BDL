from typing import List, Dict, Any, Optional
from .vector_store import VectorStore

class RAGRetriever:
    """
    Retrieval-Augmented Generation retriever.
    """
    
    def __init__(self, vector_store: VectorStore):
        """
        Initialize the RAG retriever.
        
        Args:
            vector_store: Vector store for similarity search
        """
        self.vector_store = vector_store
    
    def retrieve_context(self, query: str, max_chunks: int = 5, max_context_length: int = 2000) -> Dict[str, Any]:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: User query
            max_chunks: Maximum number of chunks to retrieve
            max_context_length: Maximum length of context in characters
            
        Returns:
            Dictionary with context and metadata
        """
        # Search for relevant chunks
        results = self.vector_store.search(query, k=max_chunks, score_threshold=0.2)
        
        if not results:
            return {
                'context': '',
                'sources': [],
                'num_chunks': 0,
                'query': query
            }
        
        # Build context from retrieved chunks
        context_parts = []
        sources = []
        current_length = 0
        
        for i, result in enumerate(results):
            chunk_content = result['content']
            chunk_metadata = result['metadata']
            
            # Check if adding this chunk would exceed max length
            if current_length + len(chunk_content) > max_context_length and context_parts:
                break
            
            # Add chunk to context
            context_parts.append(f"[Document {i+1}] {chunk_content}")
            current_length += len(chunk_content)
            
            # Track sources
            source_info = {
                'file_path': chunk_metadata.get('file_path', 'Unknown'),
                'chunk_index': chunk_metadata.get('chunk_index', 0),
                'score': result['score']
            }
            sources.append(source_info)
        
        context = '\n\n'.join(context_parts)
        
        return {
            'context': context,
            'sources': sources,
            'num_chunks': len(context_parts),
            'query': query,
            'total_context_length': len(context)
        }
    
    def format_rag_prompt(self, query: str, context: str) -> str:
        """
        Format a RAG prompt with context and query.
        
        Args:
            query: User query
            context: Retrieved context
            
        Returns:
            Formatted prompt for the LLM
        """
        if not context.strip():
            return f"""You are a helpful assistant. The user has asked a question but no relevant context was found in the documents.

User Question: {query}

Please let the user know that you don't have relevant information in the provided documents to answer their question accurately."""
        
        return f"""You are a helpful assistant that answers questions based on provided document context. Use only the information from the context below to answer the user's question. If the context doesn't contain enough information to answer the question, say so clearly.

Context from Documents:
{context}

User Question: {query}

Instructions:
- Answer based only on the provided context
- If the context doesn't have enough information, say so
- Be specific and cite relevant parts of the context
- Don't make up information not present in the context

Answer:"""
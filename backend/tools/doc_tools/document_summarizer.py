from typing import Dict, Any, List, Optional
import re
from collections import Counter

class DocumentSummarizer:
    """
    Document summarizer for creating summaries and key insights.
    """
    
    name = "document_summarizer"
    description = "Creates summaries and extracts key insights from documents"
    
    def __init__(self, llm_provider=None):
        """
        Initialize the document summarizer.
        
        Args:
            llm_provider: Optional LLM provider for AI-powered summarization
        """
        self.llm_provider = llm_provider
    
    def summarize_text(self, text: str, summary_type: str = "extractive", max_sentences: int = 3) -> Dict[str, Any]:
        """
        Summarize text content.
        
        Args:
            text: Text content to summarize
            summary_type: Type of summary ("extractive", "abstractive", "bullet_points")
            max_sentences: Maximum number of sentences in summary
            
        Returns:
            Summary results
        """
        if not text or not isinstance(text, str):
            return {'error': 'No valid text provided for summarization', 'success': False}
        
        try:
            if summary_type == "extractive":
                return self._extractive_summary(text, max_sentences)
            elif summary_type == "abstractive" and self.llm_provider:
                return self._abstractive_summary(text, max_sentences)
            elif summary_type == "bullet_points":
                return self._bullet_point_summary(text, max_sentences)
            else:
                # Default to extractive if LLM not available or unknown type
                return self._extractive_summary(text, max_sentences)
                
        except Exception as e:
            return {
                'error': f'Failed to summarize text: {str(e)}',
                'success': False
            }
    
    def _extractive_summary(self, text: str, max_sentences: int) -> Dict[str, Any]:
        """
        Create an extractive summary by selecting important sentences.
        
        Args:
            text: Text to summarize
            max_sentences: Maximum sentences in summary
            
        Returns:
            Extractive summary
        """
        sentences = self._split_into_sentences(text)
        
        if len(sentences) <= max_sentences:
            return {
                'success': True,
                'summary': text,
                'summary_type': 'extractive',
                'original_sentences': len(sentences),
                'summary_sentences': len(sentences)
            }
        
        # Score sentences based on word frequency and position
        scored_sentences = self._score_sentences(sentences, text)
        
        # Select top sentences
        top_sentences = sorted(scored_sentences, key=lambda x: x[1], reverse=True)[:max_sentences]
        
        # Sort by original order
        selected_sentences = sorted(top_sentences, key=lambda x: x[2])
        
        summary = ' '.join([sentence[0] for sentence in selected_sentences])
        
        return {
            'success': True,
            'summary': summary,
            'summary_type': 'extractive',
            'original_sentences': len(sentences),
            'summary_sentences': len(selected_sentences),
            'compression_ratio': len(summary) / len(text)
        }
    
    def _abstractive_summary(self, text: str, max_sentences: int) -> Dict[str, Any]:
        """
        Create an abstractive summary using LLM.
        
        Args:
            text: Text to summarize
            max_sentences: Maximum sentences in summary
            
        Returns:
            Abstractive summary
        """
        if not self.llm_provider:
            return self._extractive_summary(text, max_sentences)
        
        try:
            prompt = f"""Please create a concise summary of the following text in {max_sentences} sentences or fewer:

{text}

Summary:"""
            
            summary = self.llm_provider.generate(prompt)
            
            return {
                'success': True,
                'summary': summary.strip(),
                'summary_type': 'abstractive',
                'original_length': len(text),
                'summary_length': len(summary),
                'compression_ratio': len(summary) / len(text)
            }
            
        except Exception as e:
            # Fallback to extractive if LLM fails
            return self._extractive_summary(text, max_sentences)
    
    def _bullet_point_summary(self, text: str, max_points: int) -> Dict[str, Any]:
        """
        Create a bullet point summary.
        
        Args:
            text: Text to summarize
            max_points: Maximum bullet points
            
        Returns:
            Bullet point summary
        """
        sentences = self._split_into_sentences(text)
        
        if len(sentences) <= max_points:
            bullet_points = [f"• {sentence.strip()}" for sentence in sentences]
        else:
            scored_sentences = self._score_sentences(sentences, text)
            top_sentences = sorted(scored_sentences, key=lambda x: x[1], reverse=True)[:max_points]
            selected_sentences = sorted(top_sentences, key=lambda x: x[2])
            bullet_points = [f"• {sentence[0].strip()}" for sentence in selected_sentences]
        
        summary = '\n'.join(bullet_points)
        
        return {
            'success': True,
            'summary': summary,
            'summary_type': 'bullet_points',
            'original_sentences': len(sentences),
            'summary_points': len(bullet_points)
        }
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Split on sentence-ending punctuation
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        return sentences
    
    def _score_sentences(self, sentences: List[str], full_text: str) -> List[tuple]:
        """
        Score sentences for importance.
        
        Args:
            sentences: List of sentences to score
            full_text: Full text for context
            
        Returns:
            List of tuples (sentence, score, original_index)
        """
        # Get word frequencies
        words = re.findall(r'\b\w+\b', full_text.lower())
        word_freq = Counter(words)
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        scored_sentences = []
        
        for i, sentence in enumerate(sentences):
            sentence_words = re.findall(r'\b\w+\b', sentence.lower())
            sentence_words = [w for w in sentence_words if w not in stop_words]
            
            # Calculate sentence score based on word frequencies
            sentence_score = sum(word_freq[word] for word in sentence_words)
            
            # Normalize by sentence length
            if len(sentence_words) > 0:
                sentence_score = sentence_score / len(sentence_words)
            
            # Boost score for sentences at the beginning (often more important)
            position_boost = 1.0 if i < len(sentences) * 0.3 else 0.8
            sentence_score *= position_boost
            
            scored_sentences.append((sentence, sentence_score, i))
        
        return scored_sentences
    
    def extract_key_topics(self, text: str, num_topics: int = 5) -> Dict[str, Any]:
        """
        Extract key topics from text.
        
        Args:
            text: Text to analyze
            num_topics: Number of topics to extract
            
        Returns:
            Key topics
        """
        try:
            # Get word frequencies
            words = re.findall(r'\b\w+\b', text.lower())
            
            # Filter out stop words and short words
            stop_words = {
                'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
                'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
                'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
            }
            
            filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
            word_freq = Counter(filtered_words)
            
            # Get top topics
            top_topics = word_freq.most_common(num_topics)
            
            return {
                'success': True,
                'topics': [{'topic': word, 'frequency': freq} for word, freq in top_topics],
                'total_unique_words': len(word_freq)
            }
            
        except Exception as e:
            return {
                'error': f'Failed to extract topics: {str(e)}',
                'success': False
            }

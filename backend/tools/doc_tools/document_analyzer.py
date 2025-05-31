from typing import Dict, Any, List, Optional
import re
from collections import Counter

class DocumentAnalyzer:
    """
    Document analyzer for extracting insights and statistics from documents.
    """
    
    name = "document_analyzer"
    description = "Analyzes documents for insights, statistics, and key information"
    
    def __init__(self):
        """Initialize the document analyzer."""
        pass
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text content for various metrics and insights.
        
        Args:
            text: Text content to analyze
            
        Returns:
            Analysis results
        """
        if not text or not isinstance(text, str):
            return {'error': 'No valid text provided for analysis', 'success': False}
        
        try:
            analysis = {
                'success': True,
                'basic_stats': self._get_basic_statistics(text),
                'word_frequency': self._get_word_frequency(text),
                'readability': self._calculate_readability(text),
                'key_phrases': self._extract_key_phrases(text),
                'entities': self._extract_entities(text),
                'sentiment': self._analyze_sentiment(text)
            }
            
            return analysis
            
        except Exception as e:
            return {
                'error': f'Failed to analyze text: {str(e)}',
                'success': False
            }
    
    def _get_basic_statistics(self, text: str) -> Dict[str, Any]:
        """
        Calculate basic text statistics.
        
        Args:
            text: Text to analyze
            
        Returns:
            Basic statistics
        """
        # Clean text for word counting
        words = re.findall(r'\b\w+\b', text.lower())
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        paragraphs = text.split('\n\n')
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        return {
            'character_count': len(text),
            'character_count_no_spaces': len(text.replace(' ', '')),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'paragraph_count': len(paragraphs),
            'average_words_per_sentence': len(words) / len(sentences) if sentences else 0,
            'average_characters_per_word': len(text.replace(' ', '')) / len(words) if words else 0
        }
    
    def _get_word_frequency(self, text: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Get word frequency analysis.
        
        Args:
            text: Text to analyze
            top_n: Number of top words to return
            
        Returns:
            List of word frequency data
        """
        # Common stop words to filter out
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        words = re.findall(r'\b\w+\b', text.lower())
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        word_freq = Counter(filtered_words)
        top_words = word_freq.most_common(top_n)
        
        return [{'word': word, 'frequency': freq} for word, freq in top_words]
    
    def _calculate_readability(self, text: str) -> Dict[str, Any]:
        """
        Calculate readability metrics.
        
        Args:
            text: Text to analyze
            
        Returns:
            Readability metrics
        """
        # TODO: Implement readability calculations (Flesch-Kincaid, etc.)
        # For now, return basic readability indicators
        words = re.findall(r'\b\w+\b', text.lower())
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        avg_words_per_sentence = len(words) / len(sentences) if sentences else 0
        
        # Simple readability assessment
        if avg_words_per_sentence < 15:
            readability_level = "Easy"
        elif avg_words_per_sentence < 25:
            readability_level = "Medium"
        else:
            readability_level = "Difficult"
        
        return {
            'average_words_per_sentence': avg_words_per_sentence,
            'readability_level': readability_level,
            'flesch_kincaid_score': None,  # TODO: Implement
            'flesch_reading_ease': None   # TODO: Implement
        }
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """
        Extract key phrases from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of key phrases
        """
        # TODO: Implement more sophisticated key phrase extraction
        # For now, find repeated noun phrases or capitalized phrases
        
        # Find capitalized phrases (potential proper nouns)
        capitalized_phrases = re.findall(r'\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b', text)
        
        # Remove duplicates and return top phrases
        unique_phrases = list(set(capitalized_phrases))
        return unique_phrases[:10]  # Return top 10
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of entity types and their instances
        """
        # TODO: Implement NER (Named Entity Recognition)
        # For now, return basic pattern-based entity extraction
        
        # Email addresses
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        
        # Phone numbers (basic pattern)
        phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
        
        # URLs
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        
        # Dates (basic pattern)
        dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b', text)
        
        return {
            'emails': list(set(emails)),
            'phone_numbers': list(set(phones)),
            'urls': list(set(urls)),
            'dates': list(set(dates))
        }
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Perform basic sentiment analysis.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis results
        """
        # TODO: Implement proper sentiment analysis using NLP libraries
        # For now, return a basic keyword-based sentiment
        
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'positive', 'happy', 'love', 'like']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'negative', 'sad', 'hate', 'dislike', 'poor', 'worst']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "Positive"
        elif negative_count > positive_count:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        
        return {
            'sentiment': sentiment,
            'positive_indicators': positive_count,
            'negative_indicators': negative_count,
            'confidence': 'Low'  # Since this is a basic implementation
        }

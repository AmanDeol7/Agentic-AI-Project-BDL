from typing import Dict, Any, List, Optional
import os
from pathlib import Path
import logging
import re

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    TensorRT-LLM powered document processor for parsing and analyzing documents.
    """
    
    name = "document_processor"
    description = "Processes and analyzes documents using TensorRT-LLM"
    
    def __init__(self, upload_dir: Optional[Path] = None, llm_provider=None):
        """
        Initialize the document processor.
        
        Args:
            upload_dir: Directory where uploaded files are stored
            llm_provider: LLM provider for text generation (TensorRT-LLM)
        """
        self.upload_dir = upload_dir
        self.llm_provider = llm_provider
        
        # Document type handlers
        self.handlers = {
            '.pdf': self._process_pdf,
            '.txt': self._process_text,
            '.md': self._process_text,
            '.docx': self._process_word,
            '.doc': self._process_word,
            '.xlsx': self._process_excel,
            '.xls': self._process_excel,
            '.csv': self._process_csv
        }
    
    def run(self, args: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
        """
        Run the document processor tool.
        
        Args:
            args: Arguments for the tool
            context: Optional context for the tool execution
            
        Returns:
            Dictionary with processing results
        """
        try:
            action = args.get('action', 'process')
            file_path = args.get('file_path') or args.get('file')
            
            if not file_path:
                return {'error': 'No file path provided', 'success': False}
            
            # Resolve file path
            if self.upload_dir and not os.path.isabs(file_path):
                file_path = self.upload_dir / file_path
            
            if not os.path.exists(file_path):
                return {'error': f'File not found: {file_path}', 'success': False}
            
            # Route to appropriate action
            if action == 'process':
                return self._process_document(file_path, args)
            elif action == 'extract':
                return self._extract_content(file_path, args)
            elif action == 'summarize':
                return self._summarize_document(file_path, args)
            elif action == 'analyze':
                return self._analyze_document(file_path, args)
            elif action == 'question_answer':
                return self._answer_question(file_path, args)
            else:
                return {'error': f'Unknown action: {action}', 'success': False}
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Document processor error: {error_msg}")
            return {
                'error': f'Document processor error: {error_msg}',
                'success': False,
                'details': 'The document processor encountered an error. Please try again or check the file format.'
            }
    
    def _process_document(self, file_path: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a document and extract its content.
        
        Args:
            file_path: Path to the document file
            args: Additional arguments
            
        Returns:
            Processing results with extracted content
        """
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext not in self.handlers:
                return {'error': f'Unsupported file type: {file_ext}', 'success': False}
            
            # Extract content using appropriate handler
            content_result = self.handlers[file_ext](file_path)
            
            if not content_result.get('success', False):
                return content_result
            
            content = content_result.get('content', '')
            
            # Add basic document info
            result = {
                'success': True,
                'message': f'Successfully processed {file_ext} document',
                'file_path': str(file_path),
                'file_type': file_ext[1:],  # Remove dot
                'content_length': len(content),
                'content_preview': content[:300] + '...' if len(content) > 300 else content,
                'word_count': len(content.split()) if content else 0,
                'extracted_content': content
            }
            
            return result
            
        except Exception as e:
            return {'error': f'Failed to process document: {str(e)}', 'success': False}
    
    def _extract_content(self, file_path: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract raw content from a document.
        
        Args:
            file_path: Path to the document file
            args: Additional arguments
            
        Returns:
            Extracted content
        """
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext not in self.handlers:
                return {'error': f'Unsupported file type: {file_ext}', 'success': False}
            
            # Extract content using appropriate handler
            result = self.handlers[file_ext](file_path)
            
            if result.get('success', False):
                result['action'] = 'extract'
                result['message'] = f'Content extracted from {file_ext} document'
            
            return result
            
        except Exception as e:
            return {'error': f'Failed to extract content: {str(e)}', 'success': False}
    
    def _summarize_document(self, file_path: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Summarize a document using TensorRT-LLM.
        
        Args:
            file_path: Path to the document file
            args: Additional arguments
            
        Returns:
            Document summary
        """
        try:
            # First extract content
            content_result = self._extract_content(file_path, args)
            
            if not content_result.get('success', False):
                return content_result
            
            content = content_result.get('content', '')
            
            if not content.strip():
                return {'error': 'No content found to summarize', 'success': False}
            
            # Use TensorRT-LLM for summarization
            if self.llm_provider:
                summary_prompt = f"""
Please provide a concise summary of the following document content:

Document Content:
{content[:2000]}  # Limit to avoid token limits

Provide a clear, structured summary highlighting the main points, key information, and important details.
"""
                summary = self.llm_provider.generate(summary_prompt)
                
                return {
                    'success': True,
                    'message': 'Document summarized successfully',
                    'file_path': str(file_path),
                    'summary': summary,
                    'original_length': len(content),
                    'summary_length': len(summary)
                }
            else:
                # Fallback simple summarization
                sentences = re.split(r'[.!?]+', content)
                important_sentences = sentences[:3]  # Take first 3 sentences
                simple_summary = '. '.join(s.strip() for s in important_sentences if s.strip())
                
                return {
                    'success': True,
                    'message': 'Document summarized (basic method)',
                    'file_path': str(file_path),
                    'summary': simple_summary,
                    'original_length': len(content),
                    'note': 'Basic summarization used (LLM not available)'
                }
                
        except Exception as e:
            return {'error': f'Failed to summarize document: {str(e)}', 'success': False}
    
    def _analyze_document(self, file_path: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a document using TensorRT-LLM.
        
        Args:
            file_path: Path to the document file
            args: Additional arguments
            
        Returns:
            Document analysis
        """
        try:
            # First extract content
            content_result = self._extract_content(file_path, args)
            
            if not content_result.get('success', False):
                return content_result
            
            content = content_result.get('content', '')
            
            if not content.strip():
                return {'error': 'No content found to analyze', 'success': False}
            
            # Use TensorRT-LLM for analysis
            if self.llm_provider:
                analysis_prompt = f"""
Please analyze the following document and provide insights:

Document Content:
{content[:2000]}  # Limit to avoid token limits

Please provide:
1. Document type/category
2. Main topics covered
3. Key entities mentioned (people, places, organizations)
4. Sentiment/tone
5. Important dates or numbers
6. Action items or conclusions (if any)

Provide a structured analysis.
"""
                analysis = self.llm_provider.generate(analysis_prompt)
                
                return {
                    'success': True,
                    'message': 'Document analyzed successfully',
                    'file_path': str(file_path),
                    'analysis': analysis,
                    'content_length': len(content)
                }
            else:
                # Fallback basic analysis
                word_count = len(content.split())
                char_count = len(content)
                paragraphs = len([p for p in content.split('\n\n') if p.strip()])
                
                return {
                    'success': True,
                    'message': 'Document analyzed (basic method)',
                    'file_path': str(file_path),
                    'analysis': {
                        'word_count': word_count,
                        'character_count': char_count,
                        'paragraph_count': paragraphs,
                        'estimated_reading_time': f"{word_count // 200} minutes"
                    },
                    'note': 'Basic analysis used (LLM not available)'
                }
                
        except Exception as e:
            return {'error': f'Failed to analyze document: {str(e)}', 'success': False}

    def _answer_question(self, file_path: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Answer a question about a document using TensorRT-LLM.
        
        Args:
            file_path: Path to the document file
            args: Additional arguments including the question
            
        Returns:
            Answer to the question
        """
        try:
            question = args.get('question', '')
            
            if not question:
                return {'error': 'No question provided', 'success': False}
            
            # First extract content
            content_result = self._extract_content(file_path, args)
            
            if not content_result.get('success', False):
                return content_result
            
            content = content_result.get('content', '')
            
            if not content.strip():
                return {'error': 'No content found to answer question about', 'success': False}
            
            # Use TensorRT-LLM for question answering
            if self.llm_provider:
                qa_prompt = f"""
Based on the following document content, please answer the user's question accurately and comprehensively.

Document Content:
{content[:2500]}  # Provide more context for Q&A

User Question: {question}

Please provide a detailed answer based solely on the information available in the document. If the information is not available in the document, please state that clearly.
"""
                answer = self.llm_provider.generate(qa_prompt)
                
                return {
                    'success': True,
                    'message': 'Question answered successfully',
                    'file_path': str(file_path),
                    'question': question,
                    'answer': answer,
                    'content_length': len(content)
                }
            else:
                # Fallback simple search
                keywords = question.lower().split()
                relevant_sentences = []
                
                sentences = content.split('.')
                for sentence in sentences:
                    if any(keyword in sentence.lower() for keyword in keywords):
                        relevant_sentences.append(sentence.strip())
                
                if relevant_sentences:
                    answer = '. '.join(relevant_sentences[:3])  # Take first 3 relevant sentences
                else:
                    answer = "I couldn't find specific information related to your question in the document."
                
                return {
                    'success': True,
                    'message': 'Question answered (basic search)',
                    'file_path': str(file_path),
                    'question': question,
                    'answer': answer,
                    'note': 'Basic keyword search used (LLM not available)'
                }
                
        except Exception as e:
            return {'error': f'Failed to answer question: {str(e)}', 'success': False}
    
    # Document type handlers
    def _process_text(self, file_path: str) -> Dict[str, Any]:
        """Process text files (.txt, .md)"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return {
                'success': True,
                'content': content,
                'file_type': 'text'
            }
        except Exception as e:
            return {'error': f'Failed to read text file: {str(e)}', 'success': False}
    
    def _process_pdf(self, file_path: str) -> Dict[str, Any]:
        """Process PDF files using pdfplumber"""
        try:
            import pdfplumber
            
            text_content = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            
            content = '\n\n'.join(text_content)
            
            return {
                'success': True,
                'content': content,
                'file_type': 'pdf',
                'num_pages': len(text_content)
            }
        except ImportError:
            return {'error': 'pdfplumber not available. Install with: pip install pdfplumber', 'success': False}
        except Exception as e:
            return {'error': f'Failed to process PDF: {str(e)}', 'success': False}
    
    def _process_word(self, file_path: str) -> Dict[str, Any]:
        """Process Word documents (.docx, .doc)"""
        try:
            from docx import Document
            
            doc = Document(file_path)
            content = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    content.append(paragraph.text)
            
            text_content = '\n\n'.join(content)
            
            return {
                'success': True,
                'content': text_content,
                'file_type': 'word',
                'num_paragraphs': len(content)
            }
        except ImportError:
            return {'error': 'python-docx not available. Install with: pip install python-docx', 'success': False}
        except Exception as e:
            return {'error': f'Failed to process Word document: {str(e)}', 'success': False}
    
    def _process_excel(self, file_path: str) -> Dict[str, Any]:
        """Process Excel files (.xlsx, .xls)"""
        try:
            import pandas as pd
            
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)
            content = []
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                content.append(f"Sheet: {sheet_name}")
                content.append(df.to_string())
                content.append("")
            
            text_content = '\n'.join(content)
            
            return {
                'success': True,
                'content': text_content,
                'file_type': 'excel',
                'num_sheets': len(excel_file.sheet_names)
            }
        except ImportError:
            return {'error': 'pandas not available. Install with: pip install pandas openpyxl', 'success': False}
        except Exception as e:
            return {'error': f'Failed to process Excel file: {str(e)}', 'success': False}
    
    def _process_csv(self, file_path: str) -> Dict[str, Any]:
        """Process CSV files"""
        try:
            import pandas as pd
            
            df = pd.read_csv(file_path)
            content = df.to_string()
            
            return {
                'success': True,
                'content': content,
                'file_type': 'csv',
                'num_rows': len(df),
                'num_columns': len(df.columns)
            }
        except ImportError:
            return {'error': 'pandas not available. Install with: pip install pandas', 'success': False}
        except Exception as e:
            return {'error': f'Failed to process CSV file: {str(e)}', 'success': False}

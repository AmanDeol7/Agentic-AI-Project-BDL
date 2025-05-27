"""
Tool for loading and extracting content from PDF files.
"""
from typing import Dict, Any, List, Optional
import pdfplumber
import os
from pathlib import Path
import re

class PDFLoader:
    """
    Tool for loading and extracting content from PDF files.
    """
    
    name = "pdf_loader"
    description = "Extracts text content from PDF files"
    
    def __init__(self, upload_dir: Optional[Path] = None):
        """
        Initialize the PDF loader.
        
        Args:
            upload_dir: Directory where uploaded files are stored
        """
        self.upload_dir = upload_dir
    
    def run(self, args: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
        """
        Run the PDF loader tool.
        
        Args:
            args: Arguments for the tool, must contain 'file_path' or 'file'
            context: Optional context for the tool execution
            
        Returns:
            Dictionary with extracted text content
        """
        file_path = args.get('file_path') or args.get('file')
        
        if not file_path:
            return {"error": "No file path provided"}
        
        # If a relative path is provided and upload_dir is set, combine them
        if self.upload_dir and not os.path.isabs(file_path):
            file_path = self.upload_dir / file_path
        
        try:
            # Extract text and metadata
            text_content, metadata = self._extract_text_and_metadata(file_path)
            
            return {
                "text": text_content,
                "num_pages": len(text_content) if isinstance(text_content, list) else 1,
                "file_path": str(file_path),
                "metadata": metadata
            }
        except Exception as e:
            return {"error": f"Failed to extract text from PDF: {str(e)}"}
    
    def _extract_text_and_metadata(self, file_path: str) -> tuple[List[str], Dict[str, Any]]:
        """
        Extract text and metadata from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Tuple of (list of text content per page, metadata dictionary)
        """
        text_results = []
        metadata = {
            "title": None,
            "author": None,
            "creation_date": None,
            "modification_date": None,
            "page_count": 0,
            "file_size": os.path.getsize(file_path)
        }
        
        with pdfplumber.open(file_path) as pdf:
            # Extract metadata if available
            if pdf.metadata:
                metadata.update({
                    "title": pdf.metadata.get("Title"),
                    "author": pdf.metadata.get("Author"),
                    "creation_date": pdf.metadata.get("CreationDate"),
                    "modification_date": pdf.metadata.get("ModDate")
                })
            
            metadata["page_count"] = len(pdf.pages)
            
            # Extract text from each page with improved formatting
            for page in pdf.pages:
                # Extract text with layout preservation
                text = page.extract_text(layout=True) or ""
                
                # Clean up the text
                text = self._clean_text(text)
                
                # Add page number
                text = f"--- Page {len(text_results) + 1} ---\n{text}"
                
                text_results.append(text)
        
        return text_results, metadata
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and format extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned and formatted text
        """
        if not text:
            return ""
        
        # Replace multiple newlines with a single one
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Replace multiple spaces with a single one
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove any non-printable characters except newlines
        text = ''.join(char for char in text if char.isprintable() or char == '\n')
        
        # Ensure proper spacing around punctuation
        text = re.sub(r'([.,!?;:])([^\s])', r'\1 \2', text)
        
        # Remove any leading/trailing whitespace
        text = text.strip()
        
        return text
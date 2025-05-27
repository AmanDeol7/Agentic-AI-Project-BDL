"""
Tool for loading and extracting content from PDF files.
"""
from typing import Dict, Any, List, Optional
import pdfplumber
import os
from pathlib import Path

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
            text_content = self._extract_text(file_path)
            return {
                "text": text_content,
                "num_pages": len(text_content) if isinstance(text_content, list) else 1,
                "file_path": str(file_path)
            }
        except Exception as e:
            return {"error": f"Failed to extract text from PDF: {str(e)}"}
    
    def _extract_text(self, file_path: str) -> List[str]:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of text content per page
        """
        results = []
        
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                results.append(text)
        
        return results
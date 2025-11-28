"""Document processor interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class IDocumentProcessor(ABC):
    """
    Interface for document processing.
    
    Extracts text from various file formats (PDF, DOCX, etc.)
    """
    
    @abstractmethod
    async def process_file(self, file_path: str) -> str:
        """
        Process file and extract text.
        
        Args:
            file_path: Path to file
            
        Returns:
            Extracted text content
        """
        pass
    
    @abstractmethod
    async def process_bytes(self, file_bytes: bytes, mime_type: str) -> str:
        """
        Process file bytes and extract text.
        
        Args:
            file_bytes: File content as bytes
            mime_type: MIME type of file
            
        Returns:
            Extracted text content
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> list:
        """
        Get list of supported file formats.
        
        Returns:
            List of supported MIME types or extensions
        """
        pass

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class OCRResult:
    """Result from OCR processing."""
    text: str
    backend: str
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "backend": self.backend,
            "confidence": self.confidence,
            "metadata": self.metadata or {},
            "error": self.error
        }


class BaseBackend(ABC):
    """Base class for OCR backends."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize backend with configuration."""
        self.config = config
        self.name = self.__class__.__name__.lower().replace("backend", "")
    
    @abstractmethod
    async def process_file(self, file_path: str, **kwargs) -> OCRResult:
        """
        Process a file and return OCR results.
        
        Args:
            file_path: Path to the file to process
            **kwargs: Additional backend-specific options
            
        Returns:
            OCRResult with extracted text and metadata
        """
        pass
    
    @abstractmethod
    async def process_image(self, image_data: bytes, **kwargs) -> OCRResult:
        """
        Process image data and return OCR results.
        
        Args:
            image_data: Raw image bytes
            **kwargs: Additional backend-specific options
            
        Returns:
            OCRResult with extracted text and metadata
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if backend is available and configured."""
        pass
    
    def get_supported_formats(self) -> list[str]:
        """Return list of supported file formats."""
        return ["pdf", "png", "jpg", "jpeg", "tiff", "bmp"]
    
    async def process_with_fallback(
        self, 
        file_path: Optional[str] = None,
        image_data: Optional[bytes] = None,
        **kwargs
    ) -> OCRResult:
        """
        Process with automatic error handling.
        
        Args:
            file_path: Path to file (optional)
            image_data: Image bytes (optional)
            **kwargs: Additional options
            
        Returns:
            OCRResult with error information if processing fails
        """
        try:
            if file_path:
                return await self.process_file(file_path, **kwargs)
            elif image_data:
                return await self.process_image(image_data, **kwargs)
            else:
                return OCRResult(
                    text="",
                    backend=self.name,
                    error="No file_path or image_data provided"
                )
        except Exception as e:
            return OCRResult(
                text="",
                backend=self.name,
                error=f"Processing failed: {str(e)}"
            )
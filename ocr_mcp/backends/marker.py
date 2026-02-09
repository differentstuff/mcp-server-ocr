import os
from typing import Dict, Any
from .base import BaseBackend, OCRResult


class MarkerBackend(BaseBackend):
    """Marker OCR backend - local, CPU-based OCR."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.batch_size = config.get("batch_size", 1)
    
    def is_available(self) -> bool:
        """Check if Marker is available."""
        try:
            import marker
            return True
        except ImportError:
            return False
    
    async def process_file(self, file_path: str, **kwargs) -> OCRResult:
        """
        Process a file using Marker.
        
        Args:
            file_path: Path to PDF or image file
            **kwargs: Additional options (max_pages, etc.)
            
        Returns:
            OCRResult with extracted text
        """
        try:
            from marker.convert import convert_single_pdf
            from marker.models import load_all_models
            
            # Load models (cached after first call)
            model_lst = load_all_models()
            
            # Convert PDF
            full_text, images, out_meta = convert_single_pdf(
                file_path,
                model_lst,
                batch_size=self.batch_size
            )
            
            return OCRResult(
                text=full_text,
                backend=self.name,
                confidence=0.85,  # Marker typically has high confidence
                metadata={
                    "pages_processed": len(images),
                    "format": "pdf",
                    "local": True
                }
            )
            
        except Exception as e:
            return OCRResult(
                text="",
                backend=self.name,
                error=f"Marker processing failed: {str(e)}"
            )
    
    async def process_image(self, image_data: bytes, **kwargs) -> OCRResult:
        """
        Process image data using Marker.
        
        Args:
            image_data: Raw image bytes
            **kwargs: Additional options
            
        Returns:
            OCRResult with extracted text
        """
        try:
            import tempfile
            from PIL import Image
            import io
            
            # Save image to temp file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp.write(image_data)
                tmp_path = tmp.name
            
            try:
                # Process as file
                result = await self.process_file(tmp_path, **kwargs)
                return result
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    
        except Exception as e:
            return OCRResult(
                text="",
                backend=self.name,
                error=f"Marker image processing failed: {str(e)}"
            )
    
    def get_supported_formats(self) -> list[str]:
        """Marker supports PDF and images."""
        return ["pdf", "png", "jpg", "jpeg", "tiff", "bmp", "webp"]
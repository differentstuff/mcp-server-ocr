import base64
import httpx
from typing import Dict, Any
from .base import BaseBackend, OCRResult


class DeepSeekBackend(BaseBackend):
    """DeepSeek API OCR backend."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.api_timeout = config.get("api_timeout", 30)
        self.max_retries = config.get("max_retries", 3)
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
    
    def is_available(self) -> bool:
        """Check if DeepSeek API is configured."""
        return bool(self.api_key)
    
    async def process_file(self, file_path: str, **kwargs) -> OCRResult:
        """
        Process a file using DeepSeek API.
        
        Args:
            file_path: Path to PDF or image file
            **kwargs: Additional options
            
        Returns:
            OCRResult with extracted text
        """
        try:
            # Read file and encode as base64
            with open(file_path, "rb") as f:
                file_data = f.read()
            
            return await self.process_image(file_data, **kwargs)
            
        except Exception as e:
            return OCRResult(
                text="",
                backend=self.name,
                error=f"DeepSeek file processing failed: {str(e)}"
            )
    
    async def process_image(self, image_data: bytes, **kwargs) -> OCRResult:
        """
        Process image data using DeepSeek API.
        
        Args:
            image_data: Raw image bytes
            **kwargs: Additional options
            
        Returns:
            OCRResult with extracted text
        """
        try:
            # Encode image as base64
            base64_image = base64.b64encode(image_data).decode("utf-8")
            
            # Prepare API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract all text from this image. Preserve the structure and formatting as much as possible. If there is handwriting, transcribe it accurately. Return only the extracted text without any additional commentary."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 4000,
                "temperature": 0.1
            }
            
            # Make API call with retries
            async with httpx.AsyncClient(timeout=self.api_timeout) as client:
                for attempt in range(self.max_retries):
                    try:
                        response = await client.post(
                            self.base_url,
                            headers=headers,
                            json=payload
                        )
                        response.raise_for_status()
                        
                        result = response.json()
                        text = result["choices"][0]["message"]["content"]
                        
                        return OCRResult(
                            text=text,
                            backend=self.name,
                            confidence=0.90,  # DeepSeek typically has high accuracy
                            metadata={
                                "model": "deepseek-chat",
                                "api": True,
                                "attempts": attempt + 1
                            }
                        )
                        
                    except httpx.HTTPStatusError as e:
                        if attempt == self.max_retries - 1:
                            raise
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
        except Exception as e:
            return OCRResult(
                text="",
                backend=self.name,
                error=f"DeepSeek API processing failed: {str(e)}"
            )
    
    def get_supported_formats(self) -> list[str]:
        """DeepSeek supports images via vision API."""
        return ["png", "jpg", "jpeg", "webp", "gif"]
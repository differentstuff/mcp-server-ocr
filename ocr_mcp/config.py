import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration settings for OCR MCP server."""
    
    # API Keys (optional - only required if backend is enabled)
    MISTRAL_API_KEY: Optional[str] = os.getenv("MISTRAL_API_KEY")
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    
    # Backend configuration
    # Default: marker (local) and mistral (API fallback)
    ENABLED_BACKENDS: List[str] = os.getenv(
        "ENABLED_BACKENDS", 
        "marker,mistral"
    ).split(",")
    
    DEFAULT_BACKEND: str = os.getenv("DEFAULT_BACKEND", "marker")
    
    # Processing settings
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    TIMEOUT_SECONDS: int = int(os.getenv("TIMEOUT_SECONDS", "120"))
    
    # Marker settings
    MARKER_BATCH_SIZE: int = int(os.getenv("MARKER_BATCH_SIZE", "1"))
    
    # API settings
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    API_MAX_RETRIES: int = int(os.getenv("API_MAX_RETRIES", "3"))
    
    @classmethod
    def validate(cls) -> tuple[bool, List[str]]:
        """
        Validate configuration and return (is_valid, errors).
        
        Only validates API keys for backends that are actually enabled.
        """
        errors = []
        
        # Validate backends
        valid_backends = {"marker", "deepseek", "mistral"}
        for backend in cls.ENABLED_BACKENDS:
            if backend not in valid_backends:
                errors.append(f"Invalid backend: {backend}")
        
        # Validate default backend
        if cls.DEFAULT_BACKEND not in cls.ENABLED_BACKENDS:
            errors.append(
                f"Default backend '{cls.DEFAULT_BACKEND}' not in enabled backends"
            )
        
        # Validate API keys ONLY for enabled backends
        if "deepseek" in cls.ENABLED_BACKENDS and not cls.DEEPSEEK_API_KEY:
            errors.append(
                "DeepSeek backend is enabled but DEEPSEEK_API_KEY is not set. "
                "Either add the API key or remove 'deepseek' from ENABLED_BACKENDS."
            )
        
        if "mistral" in cls.ENABLED_BACKENDS and not cls.MISTRAL_API_KEY:
            errors.append(
                "Mistral backend is enabled but MISTRAL_API_KEY is not set. "
                "Either add the API key or remove 'mistral' from ENABLED_BACKENDS."
            )
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_backend_priority(cls) -> List[str]:
        """Get backends in priority order."""
        # Ensure default backend is first
        backends = cls.ENABLED_BACKENDS.copy()
        if cls.DEFAULT_BACKEND in backends:
            backends.remove(cls.DEFAULT_BACKEND)
            backends.insert(0, cls.DEFAULT_BACKEND)
        return backends


settings = Settings()
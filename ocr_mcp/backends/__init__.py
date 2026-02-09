from .base import BaseBackend, OCRResult
from .marker import MarkerBackend
from .deepseek import DeepSeekBackend
from .mistral import MistralBackend

__all__ = [
    "BaseBackend",
    "OCRResult",
    "MarkerBackend",
    "DeepSeekBackend",
    "MistralBackend",
]


def get_backend(backend_name: str, config: dict) -> BaseBackend:
    """Factory function to get backend instance."""
    backends = {
        "marker": MarkerBackend,
        "deepseek": DeepSeekBackend,
        "mistral": MistralBackend,
    }
    
    backend_class = backends.get(backend_name.lower())
    if not backend_class:
        raise ValueError(f"Unknown backend: {backend_name}")
    
    return backend_class(config)
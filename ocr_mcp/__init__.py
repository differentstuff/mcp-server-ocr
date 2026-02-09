"""OCR MCP Server - Multi-backend OCR for LibreChat."""

__version__ = "0.1.0"
__author__ = "LibreChat Community"

from .config import settings
from .backends import BaseBackend, OCRResult

__all__ = ["settings", "BaseBackend", "OCRResult"]
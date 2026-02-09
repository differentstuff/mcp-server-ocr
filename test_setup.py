#!/usr/bin/env python3
"""Test script to verify OCR MCP server setup."""

import sys
import os


def test_imports():
    """Test that all imports work."""
    print("Testing imports...")
    try:
        from ocr_mcp import settings
        from ocr_mcp.backends import BaseBackend, OCRResult
        from ocr_mcp.backends import MarkerBackend, DeepSeekBackend, MistralBackend
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_config():
    """Test configuration."""
    print("\\nTesting configuration...")
    from ocr_mcp.config import settings
    
    is_valid, errors = settings.validate()
    
    if is_valid:
        print("✓ Configuration valid")
        print(f"  Enabled backends: {', '.join(settings.ENABLED_BACKENDS)}")
        print(f"  Default backend: {settings.DEFAULT_BACKEND}")
        return True
    else:
        print("✗ Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        return False


def test_backends():
    """Test backend availability."""
    print("\\nTesting backends...")
    from ocr_mcp.backends import MarkerBackend, DeepSeekBackend, MistralBackend
    from ocr_mcp.config import settings
    
    backends = {
        "marker": MarkerBackend,
        "deepseek": DeepSeekBackend,
        "mistral": MistralBackend,
    }
    
    available = []
    for name, backend_class in backends.items():
        config = {
            "api_key": getattr(settings, f"{name.upper()}_API_KEY", None),
            "api_timeout": settings.API_TIMEOUT,
            "max_retries": settings.API_MAX_RETRIES,
            "batch_size": settings.MARKER_BATCH_SIZE,
        }
        backend = backend_class(config)
        if backend.is_available():
            available.append(name)
            print(f"✓ {name.capitalize()} backend available")
        else:
            print(f"✗ {name.capitalize()} backend not available")
    
    if available:
        print(f"\\n✓ {len(available)} backend(s) available: {', '.join(available)}")
        return True
    else:
        print("\\n✗ No backends available")
        return False


def test_mcp_server():
    """Test MCP server can be imported."""
    print("\\nTesting MCP server...")
    try:
        from ocr_mcp.server import app
        print("✓ MCP server imported successfully")
        return True
    except Exception as e:
        print(f"✗ MCP server import failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("OCR MCP Server Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_backends,
        test_mcp_server,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\\n✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"✓ All {total} tests passed!")
        print("\\nYour OCR MCP server is ready to use.")
        print("\\nNext steps:")
        print("1. Configure LibreChat to use the MCP server")
        print("2. Restart LibreChat")
        print("3. Test with a PDF or image file")
        return 0
    else:
        print(f"✗ {total - passed} of {total} tests failed")
        print("\\nPlease fix the issues above before using the server.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
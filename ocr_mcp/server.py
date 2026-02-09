import asyncio
import sys
from typing import Any, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from .config import settings
from .backends import get_backend, OCRResult


# Initialize MCP server
app = Server("ocr-mcp")


def get_backends():
    """Get configured backends in priority order."""
    backends = []
    for backend_name in settings.get_backend_priority():
        config = {
            "api_key": getattr(settings, f"{backend_name.upper()}_API_KEY", None),
            "api_timeout": settings.API_TIMEOUT,
            "max_retries": settings.API_MAX_RETRIES,
            "batch_size": settings.MARKER_BATCH_SIZE,
        }
        backend = get_backend(backend_name, config)
        if backend.is_available():
            backends.append(backend)
    return backends


async def process_with_fallback(
    file_path: Optional[str] = None,
    image_data: Optional[bytes] = None,
    backend: Optional[str] = None
) -> OCRResult:
    """
    Process OCR with automatic fallback between backends.
    
    Args:
        file_path: Path to file (optional)
        image_data: Image bytes (optional)
        backend: Specific backend to use (optional)
        
    Returns:
        OCRResult with extracted text
    """
    backends = get_backends()
    
    if not backends:
        return OCRResult(
            text="",
            backend="none",
            error="No available OCR backends configured"
        )
    
    # If specific backend requested, try only that one
    if backend:
        for b in backends:
            if b.name == backend.lower():
                result = await b.process_with_fallback(
                    file_path=file_path,
                    image_data=image_data
                )
                return result
        return OCRResult(
            text="",
            backend="none",
            error=f"Requested backend '{backend}' not available"
        )
    
    # Try each backend in priority order
    errors = []
    for b in backends:
        result = await b.process_with_fallback(
            file_path=file_path,
            image_data=image_data
        )
        
        if result.error is None and result.text:
            return result
        
        if result.error:
            errors.append(f"{b.name}: {result.error}")
    
    # All backends failed
    return OCRResult(
        text="",
        backend="none",
        error=f"All backends failed: {'; '.join(errors)}"
    )


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available OCR tools."""
    return [
        Tool(
            name="ocr",
            description="Extract text from PDF files or images using OCR. Supports multiple backends (Marker, DeepSeek, Mistral) with automatic fallback.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the PDF or image file to process"
                    },
                    "backend": {
                        "type": "string",
                        "description": "Specific backend to use (marker, deepseek, mistral). If not specified, uses default with automatic fallback.",
                        "enum": ["marker", "deepseek", "mistral"]
                    }
                }
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    if name == "ocr":
        file_path = arguments.get("file_path")
        backend = arguments.get("backend")
        
        if not file_path:
            return [TextContent(
                type="text",
                text="Error: file_path is required"
            )]
        
        result = await process_with_fallback(
            file_path=file_path,
            backend=backend
        )
        
        if result.error:
            return [TextContent(
                type="text",
                text=f"Error: {result.error}"
            )]
        
        # Format output
        output = f"Backend used: {result.backend}\\n"
        if result.confidence:
            output += f"Confidence: {result.confidence:.2%}\\n"
        output += f"\\nExtracted Text:\\n{'-' * 40}\\n{result.text}"
        
        return [TextContent(
            type="text",
            text=output
        )]
    
    return [TextContent(
        type="text",
        text=f"Unknown tool: {name}"
    )]


async def main():
    """Main entry point."""
    # Validate configuration
    is_valid, errors = settings.validate()
    if not is_valid:
        print("Configuration errors:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
    
    # Print configuration info
    print(f"OCR MCP Server starting...", file=sys.stderr)
    print(f"Enabled backends: {', '.join(settings.ENABLED_BACKENDS)}", file=sys.stderr)
    print(f"Default backend: {settings.DEFAULT_BACKEND}", file=sys.stderr)
    
    # List available backends
    backends = get_backends()
    print(f"Available backends: {', '.join([b.name for b in backends])}", file=sys.stderr)
    
    # Start server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
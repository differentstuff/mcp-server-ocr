# OCR MCP Server

Multi-backend OCR MCP server for LibreChat with support for Marker (local), DeepSeek API, and Mistral API.

## Features

- **Multiple Backends**: Marker (local, free), DeepSeek API, Mistral API
- **Automatic Fallback**: Seamlessly falls back to next backend on failure
- **Flexible Configuration**: Environment-based configuration
- **Cost-Effective**: Use local Marker for simple docs, APIs for complex handwriting
- **Easy Integration**: Works with LibreChat MCP
- **Optional Backends**: Enable only the backends you need

## Quick Start

### Minimal Setup (Marker + Mistral)

```bash
# Install
pip install -r requirements.txt

# Configure (only Mistral key required)
echo 'MISTRAL_API_KEY=your-key-here' > .env

# Test
python -m ocr_mcp.server
```

### LibreChat Configuration

```yaml
mcpServers:
  ocr:
    command: "python"
    args: ["-m", "ocr_mcp.server"]
    env:
      MISTRAL_API_KEY: "your-mistral-key-here"
      ENABLED_BACKENDS: "marker,mistral"
      DEFAULT_BACKEND: "marker"
```

## Configuration

### Environment Variables

```bash
# API Keys (only required for enabled backends)
MISTRAL_API_KEY=your-mistral-key-here      # Required if mistral enabled
DEEPSEEK_API_KEY=your-deepseek-key-here    # Optional - only if deepseek enabled

# Backend Configuration
ENABLED_BACKENDS=marker,mistral            # Comma-separated list
DEFAULT_BACKEND=marker                     # Default backend to use

# Processing Settings
MAX_FILE_SIZE_MB=50                        # Maximum file size
TIMEOUT_SECONDS=120                        # Processing timeout
API_TIMEOUT=30                             # API call timeout
API_MAX_RETRIES=3                          # API retry attempts
MARKER_BATCH_SIZE=1                        # Marker batch size
```

### Backend Options

**Marker Only (No API keys needed):**
```yaml
ENABLED_BACKENDS: "marker"
DEFAULT_BACKEND: "marker"
```

**Marker + Mistral (Recommended):**
```yaml
MISTRAL_API_KEY: "your-key"
ENABLED_BACKENDS: "marker,mistral"
DEFAULT_BACKEND: "marker"
```

**All Backends (When you have DeepSeek key):**
```yaml
MISTRAL_API_KEY: "your-mistral-key"
DEEPSEEK_API_KEY: "your-deepseek-key"
ENABLED_BACKENDS: "marker,deepseek,mistral"
DEFAULT_BACKEND: "marker"
```

## Usage

### In LibreChat Assistant

**Auto-select backend:**
```
Extract text from this PDF
```

**Specify backend:**
```
Use Mistral to extract text from this handwritten page
```

**Batch processing:**
```
Process all uploaded PDFs with Marker first, use Mistral for pages with tables
```

### Available Tools

- **ocr**: Extract text from PDF files or images
  - `file_path` (required): Path to the file
  - `backend` (optional): Specific backend to use (marker, deepseek, mistral)

## Backend Details

### Marker (Local)
- **Pros**: Free, fast, CPU-only, no API costs
- **Best for**: Text-heavy documents, clean PDFs
- **Limitations**: Struggles with handwriting and complex layouts
- **Requirements**: No API key needed

### Mistral API (Pixtral)
- **Pros**: Best OCR accuracy, excellent with complex layouts
- **Best for**: Tables, forms, mixed content, handwriting
- **Cost**: API usage based
- **Requirements**: Valid Mistral API key

### DeepSeek API
- **Pros**: Excellent handwriting recognition, affordable
- **Best for**: Handwritten notes, marked-up documents
- **Cost**: API usage based
- **Requirements**: Valid DeepSeek API key (optional)

## Adding DeepSeek Later

When you're ready to enable DeepSeek:

1. Get API key from: https://platform.deepseek.com/api_keys
2. Add to your configuration:
   ```yaml
   DEEPSEEK_API_KEY: "your-deepseek-key-here"
   ENABLED_BACKENDS: "marker,deepseek,mistral"
   ```
3. Restart LibreChat

The server will automatically detect and use DeepSeek when available.

## Troubleshooting

### MCP server not appearing
- Check `librechat.yaml` indentation (YAML is whitespace-sensitive)
- Verify API keys are set correctly
- Check Docker logs: `docker-compose logs -f`

### "Backend not available" error
- Ensure `ENABLED_BACKENDS` matches your available API keys
- DeepSeek will be skipped if no API key is provided
- Mistral requires a valid API key if enabled
- Marker requires no extra setup

### Slow processing
- Marker runs locally (fast for simple docs)
- API calls take 2-5 seconds per page
- Consider batch processing for large books

### Marker installation issues
```bash
# Install marker-pdf separately
pip install marker-pdf

# Or install all dependencies
pip install -r requirements.txt
```

### Configuration validation errors
The server will validate your configuration on startup. Common errors:

- **"DeepSeek backend is enabled but DEEPSEEK_API_KEY is not set"**
  - Either add the API key, or remove 'deepseek' from ENABLED_BACKENDS

- **"Mistral backend is enabled but MISTRAL_API_KEY is not set"**
  - Either add the API key, or remove 'mistral' from ENABLED_BACKENDS

## Development

### Project Structure

```
ocr-mcp/
├── ocr_mcp/
│   ├── __init__.py
│   ├── server.py          # Main MCP server
│   ├── config.py          # Configuration management
│   └── backends/
│       ├── __init__.py
│       ├── base.py        # Base backend interface
│       ├── marker.py      # Marker backend
│       ├── deepseek.py    # DeepSeek API backend
│       └── mistral.py     # Mistral API backend
├── pyproject.toml
└── README.md
```

### Running from source

```bash
# Install in development mode
pip install -e .

# Run server
python -m ocr_mcp.server
```

## License

MIT License

## Contributing

Contributions welcome! Please feel free to submit issues or pull requests.
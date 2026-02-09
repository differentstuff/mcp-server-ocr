# Quick Start Guide

## 1. Install Dependencies

```bash
cd /opt/LibreChat_Data/user_workspaces/jmheck/temp/ocr-mcp
pip install -r requirements.txt
```

## 2. Configure API Keys

Edit `.env` file and add your Mistral API key:

```bash
# Get key from: https://console.mistral.ai/api-keys/
MISTRAL_API_KEY=your-mistral-key-here

# DeepSeek is optional - only add if you want to enable it later
# DEEPSEEK_API_KEY=your-deepseek-key-here
```

## 3. Test the Server

```bash
python -m ocr_mcp.server
```

You should see output like:
```
OCR MCP Server starting...
Enabled backends: marker,mistral
Default backend: marker
Available backends: marker, mistral
```

## 4. Configure LibreChat

Add to your `librechat.yaml`:

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

## 5. Restart LibreChat

```bash
docker-compose restart
```

## 6. Test in LibreChat

Create a new Assistant and try:
```
Extract text from this PDF
```

## Enabling DeepSeek Later

When you're ready to add DeepSeek:

1. Get API key from: https://platform.deepseek.com/api_keys
2. Add to `.env` or `librechat.yaml`:
   ```yaml
   DEEPSEEK_API_KEY: "your-deepseek-key-here"
   ENABLED_BACKENDS: "marker,deepseek,mistral"
   ```
3. Restart LibreChat

## Troubleshooting

### Marker not working
```bash
pip install marker-pdf
```

### Import errors
```bash
pip install -e .
```

### API key errors
- Verify Mistral key is correct
- Check API key permissions
- Ensure key has sufficient credits

### "Backend not available" error
- Check that `ENABLED_BACKENDS` matches your API keys
- DeepSeek will be skipped if no API key is provided
- Mistral requires a valid API key if enabled

## Next Steps

- Read [README.md](README.md) for full documentation
- Test with different document types
- Add DeepSeek later when needed
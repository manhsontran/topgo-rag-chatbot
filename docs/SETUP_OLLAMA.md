# 🚀 Setup Ollama - Local LLM

## Why Use Ollama?

✅ **100% Free** - No API key required, unlimited requests
✅ **Privacy** - Data stays local, nothing sent to cloud
✅ **Fast** - Runs on GPU if available, CPU also works
✅ **Offline** - Works without internet

---

## Step 1: Install Ollama

### Windows:
```bash
# Download from: https://ollama.ai/download/windows
# Run OllamaSetup.exe
```

### macOS:
```bash
# Download from: https://ollama.ai/download/mac
# Or use Homebrew:
brew install ollama
```

### Linux:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

---

## Step 2: Start Ollama

```bash
# Start Ollama server (runs in background)
ollama serve
```

**Windows**: Ollama runs automatically after installation, no need for `ollama serve`

---

## Step 3: Download Model

```bash
# Lightweight, fast model (1.5GB) - Recommended
ollama pull qwen2:1.5b

# Or larger model (4.7GB) - Better quality
ollama pull llama2

# Good Vietnamese model (2GB)
ollama pull vinallama
```

---

## Step 4: Test Ollama

```bash
# Chat directly with model
ollama run qwen2:1.5b

>>> Hello, how can you help me?
```

Press `Ctrl+D` or type `/bye` to exit.

---

## Check Installed Models

```bash
# List models
ollama list

# Sample output:
# NAME                ID              SIZE    MODIFIED
# qwen2:1.5b         abc123def       1.5 GB  2 hours ago
# llama2:latest      xyz789ghi       4.7 GB  1 day ago
```

---

## Project Configuration

`.env` file configuration:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2:1.5b
```

---

## Run Project with Ollama

```bash
# 1. Make sure Ollama is running
ollama serve  # Linux/Mac
# Windows: Runs automatically

# 2. Run API backend
python run_api.py

# 3. Run Streamlit UI
streamlit run app.py
```

---

## Troubleshooting

### Error: "Connection refused"
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running:
ollama serve  # Linux/Mac
# Windows: Restart Ollama app
```

### Error: "Model not found"
```bash
# Pull model again
ollama pull qwen2:1.5b
```

### Insufficient RAM
```bash
# Use smaller model
ollama pull qwen2:0.5b  # Only 500MB
```

---

## Recommended Models

| Model | Size | RAM | Speed | Quality |
|-------|------|-----|--------|------------|
| `qwen2:0.5b` | 500MB | 2GB | ⚡⚡⚡ | ⭐⭐ |
| `qwen2:1.5b` | 1.5GB | 4GB | ⚡⚡ | ⭐⭐⭐ |
| `llama2` | 4.7GB | 8GB | ⚡ | ⭐⭐⭐⭐ |
| `vinallama` | 2GB | 6GB | ⚡⚡ | ⭐⭐⭐⭐ (Vietnamese) |

---

## API Endpoints

Ollama API runs automatically at: `http://localhost:11434`

```bash
# Test API
curl http://localhost:11434/api/tags

# Generate text
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2:1.5b",
  "prompt": "Hello"
}'
```

---

## References

- 📖 Docs: https://github.com/ollama/ollama
- 🤖 Models: https://ollama.ai/library
- 💬 Community: https://discord.gg/ollama

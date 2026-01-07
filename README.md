# TopGo RAG Chatbot

Intelligent restaurant recommendation system using RAG (Retrieval-Augmented Generation) with **Ollama Local LLM** - Free and unlimited.

---

## Features

- **AI Chat with Ollama** - Local LLM, 100% free
- **Semantic Search** - Intelligent search with embeddings
- **Personalized Recommendations** - Based on context and preferences
- **1891+ restaurants** - Data crawled from TopGo.vn (Hanoi)
- **FastAPI Backend** + **Streamlit UI**
- **100% Local** - No API keys needed, complete privacy

---

## Quick Start

### Step 1: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Setup Ollama (Local LLM)

```bash
# Download and install Ollama: https://ollama.ai
# Windows: Run OllamaSetup.exe
# Mac: brew install ollama
# Linux: curl -fsSL https://ollama.ai/install.sh | sh

# Pull model (choose one of the following models)
ollama pull qwen2:1.5b      # Lightweight, fast model (1.5GB) - Recommended
ollama pull llama2          # Larger model (4.7GB)
ollama pull vinallama       # Vietnamese model (2GB)
```

**Detailed guide:** [docs/SETUP_OLLAMA.md](docs/SETUP_OLLAMA.md)

### Step 3: Run application

```bash
# Method 1: Use script (Windows)
.\start_all.bat

# Method 2: Run directly
streamlit run app.py
```

Open browser: **http://localhost:8501**

**Note:** 
- App works even without Ollama (search-only mode)
- To use AI chat, start Ollama: `ollama serve`
- API backend (optional): `python run_api.py`

---

## Project Structure

```
topgo-rag-chatbot/
├── data/                      # Data
│   ├── raw/                   # Raw crawled data
│   ├── processed/             # Processed data (JSON)
│   └── vector_db/             # ChromaDB vector database
│
├── src/                       # Main source code
│   ├── api/                   # FastAPI REST API
│   ├── crawlers/              # Web scraping TopGo.vn
│   ├── embeddings/            # Vector embeddings & search
│   ├── llm/                   # Ollama LLM client
│   └── rag/                   # RAG pipeline & prompts
│
├── docs/                      # Documentation
│   ├── DOCUMENTATION.md       # Complete documentation
│   ├── SETUP_OLLAMA.md        # Ollama setup guide
│   └── ...                    # Other docs
│
├── scripts/                   # Utility scripts
│   ├── setup_ollama.bat       # Automatic Ollama setup
│   └── rebuild_embeddings.py  # Rebuild vector DB
│
├── app.py                     # Streamlit UI (Main App)
├── start_all.bat              # Start all services
├── stop_all.bat               # Stop all services
├── requirements.txt           # Python dependencies
├── .env                       # Environment config
└── README.md                  # You are reading this file
```

---

## Usage

### 1. Quick Start

```bash
# Windows: Double-click or command line
.\start_all.bat

# Or run directly
streamlit run app.py
```

### 2. Chat with AI

```
User: "Find affordable Vietnamese restaurant in Cau Giay"
AI: Based on your request, I recommend:
     1. Good Restaurant - Cau Giay
        Address: 123 XYZ Street
        Price: 50k-100k/person
        Match: 95%
```

**Operating modes:**
- **Ollama ON:** Full AI chat + semantic search
- **Ollama OFF:** Semantic search only (still accurate)

### 3. Search Filters

- **Type:** Restaurant, Bar, Karaoke
- **District:** Tay Ho, Hoan Kiem, Cau Giay, Ba Dinh...
- **Price Range:** Affordable, Moderate, Premium

---

## Configuration (Simple)

`.env` file:

```env
# Ollama Configuration (Local LLM)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2:1.5b
```

---

## Tech Stack

### Backend
- **FastAPI** - REST API framework
- **ChromaDB** - Vector database
- **Sentence Transformers** - Text embeddings
- **Ollama** - Local LLM inference

### Frontend
- **Streamlit** - Interactive web UI
- **Pandas** - Data processing

### LLM & RAG
- **Ollama** - Local LLM (qwen2, llama2, vinallama)
- **Retrieval-Augmented Generation** - RAG pattern

---

## Data

- **1891 locations** from TopGo.vn
- **Types:** Restaurant, Bar, Karaoke
- **Area:** Hanoi (inner city districts)
- **Information:** Name, address, phone, price, description, ratings

---

## Development

### Crawl new data

```bash
python src/crawlers/topgo_crawler.py
```

### Rebuild embeddings

```bash
python scripts/rebuild_embeddings.py
```

### View project statistics

```bash
python scripts/project_stats.py
```

### Run API Backend (Optional)

```bash
python scripts/run_api.py
# Or: uvicorn src.api.main:app --reload
```

---

## Troubleshooting

### 1. "Ollama connection refused" error

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, restart
ollama serve  # Linux/Mac
# Windows: Restart Ollama app
```

### 2. Model not available

```bash
ollama pull qwen2:1.5b
```

### 3. Port 8000 already in use

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

---

## Additional Documentation

See more in [docs/](docs/) folder:

- [QUICKSTART_SIMPLE.md](docs/QUICKSTART_SIMPLE.md) - 3-step quickstart
- [SETUP_OLLAMA.md](docs/SETUP_OLLAMA.md) - Detailed Ollama setup
- [STREAMLIT_LOCAL.md](docs/STREAMLIT_LOCAL.md) - Streamlit guide
- [OPTIMIZATION_DONE.md](docs/OPTIMIZATION_DONE.md) - Optimizations completed
- [RAG_IMPLEMENTATION.md](docs/RAG_IMPLEMENTATION.md) - RAG pipeline
- [API_BACKEND_COMPLETE.md](docs/API_BACKEND_COMPLETE.md) - API docs

---

## To-Do

- [ ] Add more filters (cuisine type, rating)
- [ ] Multi-language support
- [ ] User feedback system
- [ ] Recommendation history
- [ ] Mobile responsive UI

---

## License

MIT License

---

## Contributors

- Your Name - Initial work

---

## Acknowledgments

- TopGo.vn - Data source
- Ollama - Local LLM framework
- ChromaDB - Vector database
- Sentence Transformers - Embeddings

---

## Support

- Docs: [SETUP_OLLAMA.md](SETUP_OLLAMA.md)
- Issues: Create an issue on GitHub
- Discord: [Ollama Community](https://discord.gg/ollama)

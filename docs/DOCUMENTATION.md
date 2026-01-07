# 📚 TopGo RAG Chatbot - Documentation

## 📖 Table of Contents

1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Installation and Running](#installation-and-running)
4. [User Guide](#user-guide)
5. [API Reference](#api-reference)
6. [Features](#features)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Introduction

TopGo RAG Chatbot is an intelligent restaurant recommendation system using:
- **RAG (Retrieval-Augmented Generation)** - Combines search and LLM
- **Ollama** - Local LLM, 100% free
- **ChromaDB** - Vector database for semantic search
- **FastAPI** - REST API backend
- **Streamlit** - User-friendly web UI

### 📊 Data
- **1,891 locations** (restaurants, bars, karaoke)
- **Source:** TopGo.vn (Hanoi)
- **Metadata:** District, type, price, cuisine, features

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                 │
└────────────┬────────────────────────────────┬────────────────┘
             │                                │
             ▼                                ▼
    ┌─────────────────┐            ┌─────────────────┐
    │  Streamlit UI   │            │   FastAPI       │
    │  (Port 8501)    │            │   (Port 8000)   │
    └────────┬────────┘            └────────┬────────┘
             │                              │
             └──────────────┬───────────────┘
                            ▼
                   ┌─────────────────┐
                   │   RAG Pipeline  │
                   │  - Query Class  │
                   │  - Filter Ext   │
                   │  - Search       │
                   │  - Generate     │
                   └────┬───────┬────┘
                        │       │
            ┌───────────┘       └──────────┐
            ▼                               ▼
   ┌─────────────────┐           ┌──────────────────┐
   │  Search Engine  │           │  Ollama Client   │
   │  - ChromaDB     │           │  - qwen2:1.5b    │
   │  - Embeddings   │           │  - Local LLM     │
   │  - Filters      │           │  (Port 11434)    │
   └─────────────────┘           └──────────────────┘
```

### 🔄 Query Flow

1. **User Input** → Streamlit/API
2. **Query Classification** → Identify question type
3. **Filter Extraction** → Extract district, type, price
4. **District Validation** → Check valid district (33 Hanoi districts)
5. **Semantic Search** → ChromaDB finds top-K restaurants
6. **Context Building** → Format data for prompt
7. **LLM Generation** → Ollama generates Vietnamese answer
8. **Response** → Return to user

---

## ⚙️ Installation and Running

### 1️⃣ Prerequisites

```bash
# Python 3.8+
python --version
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Setup Ollama (Local LLM)

**Windows:**
```bash
# Download from https://ollama.ai
# Install OllamaSetup.exe

# Pull model
ollama pull qwen2:1.5b
```

**Linux/Mac:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull qwen2:1.5b
```

### 4️⃣ Run Application

**Method 1: Automated script (Windows)**
```bash
.\start_all.bat
```

**Method 2: Manual run**
```bash
# Terminal 1: Ollama
ollama serve

# Terminal 2: FastAPI Backend
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Terminal 3: Streamlit Frontend
streamlit run app.py
```

### 5️⃣ Access

| Service | URL |
|---------|-----|
| Streamlit UI | http://localhost:8501 |
| FastAPI Backend | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Ollama | http://localhost:11434 |

---

## 📖 User Guide

### Streamlit UI

1. Open http://localhost:8501
2. Enter question in chat box
3. View results from chatbot

**Example queries:**
```
- Find Vietnamese restaurants in Hoan Kiem
- Suggest upscale bars in Tay Ho
- Find cheap buffet
- Karaoke suitable for company in Cau Giay
- Romantic Italian restaurant for dating
```

### REST API

**POST /api/chat**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find restaurant in Hoan Kiem",
    "conversation_id": "user123"
  }'
```

**GET /health**
```bash
curl http://localhost:8000/health
```

---

## 🔧 API Reference

### RAGPipeline

```python
from src.rag.pipeline import RAGPipeline

pipeline = RAGPipeline(
    model_name="qwen2:1.5b",
    base_url="http://localhost:11434"
)

response = pipeline.answer(
    query="Find restaurant in Hoan Kiem",
    top_k=5
)
```

### RestaurantSearchEngine

```python
from src.embeddings.search_engine import RestaurantSearchEngine

engine = RestaurantSearchEngine()

results = engine.search(
    query="Vietnamese restaurant",
    n_results=5,
    filters={
        'district': 'Hoan Kiem',
        'business_type': 'restaurant',
        'price_range': 'binh_dan'
    }
)
```

### OllamaClient

```python
from src.llm.ollama_client import OllamaClient

client = OllamaClient(
    model="qwen2:1.5b",
    base_url="http://localhost:11434"
)

response = client.generate(
    prompt="Introduce this restaurant...",
    system_prompt="You are an AI assistant...",
    temperature=0.7
)
```

---

## ✨ Features

### 1. Query Classification
- Automatically classify questions (restaurant query, greeting, out-of-scope)
- Keyword-based pre-classification (40+ keywords)
- Fallback to LLM classification

### 2. District Validation
- Validate 33 Hanoi districts (with and without Vietnamese diacritics)
- Reject invalid districts with helpful message
- Auto-correct common district name errors

### 3. Semantic Search
- ChromaDB vector database
- Multilingual embeddings (paraphrase-multilingual-MiniLM-L12-v2)
- Filter by: district, type, price level

### 4. LLM Generation
- Ollama local LLM (qwen2:1.5b)
- Vietnamese prompts
- No fabrication when data unavailable

### 5. Filter Support

| Filter | Values |
|--------|--------|
| `district` | Hoan Kiem, Tay Ho, Cau Giay, Ba Dinh, ... (33 districts) |
| `business_type` | restaurant, bar, karaoke |
| `price_range` | binh_dan, trung_binh, cao_cap |

---

## 🐛 Troubleshooting

### "No LLM available"

```bash
# Start Ollama
ollama serve

# Verify
curl http://localhost:11434/api/tags
```

### "Collection not found"

```bash
# Rebuild embeddings
python scripts/rebuild_embeddings.py
```

### Port already in use

```bash
# Windows - Kill process
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

### Model cannot load

```bash
# Re-pull model
ollama pull qwen2:1.5b
```

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| Query Classification | 98.4% accuracy |
| District Validation | 100% accuracy |
| Search Latency | ~100-200ms |
| LLM Generation | ~2-5s (GPU) |
| Total Response | ~3-7s |

---

## 🔒 Security

- ✅ 100% Local - No data sent externally
- ✅ No API keys required
- ✅ Input validation
- ✅ SQL injection prevention

---

## 📝 License

MIT License - Free to use

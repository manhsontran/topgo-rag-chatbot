# 🍽️ TopGo RAG Chatbot

Hệ thống gợi ý nhà hàng thông minh sử dụng RAG (Retrieval-Augmented Generation) với **Ollama Local LLM** - Miễn phí, không giới hạn.

---

## ✨ Tính năng

- 🤖 **Chat AI với Ollama** - LLM chạy local, 100% miễn phí
- 🔍 **Semantic Search** - Tìm kiếm thông minh với embeddings
- 🎯 **Gợi ý cá nhân hóa** - Dựa trên ngữ cảnh và sở thích
- 📊 **1891+ nhà hàng** - Dữ liệu crawl từ TopGo.vn (Hà Nội)
- 🌐 **FastAPI Backend** + 🎨 **Streamlit UI**
- 🔒 **100% Local** - Không cần API keys, bảo mật tuyệt đối

---

## 🚀 Quick Start

### Bước 1: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 2: Setup Ollama (LLM Local)

```bash
# Download và cài đặt Ollama: https://ollama.ai
# Windows: Chạy OllamaSetup.exe
# Mac: brew install ollama
# Linux: curl -fsSL https://ollama.ai/install.sh | sh

# Pull model (chọn 1 trong các model sau)
ollama pull qwen2:1.5b      # Model nhẹ, nhanh (1.5GB) ⭐ Khuyến nghị
ollama pull llama2          # Model lớn hơn (4.7GB)
ollama pull vinallama       # Model tiếng Việt (2GB)
```

📖 **Hướng dẫn chi tiết:** [docs/SETUP_OLLAMA.md](docs/SETUP_OLLAMA.md)

### Bước 3: Chạy ứng dụng

```bash
# Cách 1: Dùng script (Windows)
.\start_all.bat

# Cách 2: Chạy trực tiếp
streamlit run app.py
```

Mở trình duyệt: **http://localhost:8501**

**Lưu ý:** 
- ✅ App chạy được ngay cả khi Ollama chưa có (chế độ search-only)
- 🤖 Để dùng AI chat, cần khởi động Ollama: `ollama serve`
- 📊 API backend (optional): `python run_api.py`

---

## 📁 Cấu trúc Project

```
topgo-rag-chatbot/
├── data/                      # 📂 Dữ liệu
│   ├── raw/                   # Dữ liệu thô crawl được
│   ├── processed/             # Dữ liệu đã xử lý (JSON)
│   └── vector_db/             # ChromaDB vector database
│
├── src/                       # 🔧 Source code chính
│   ├── api/                   # FastAPI REST API
│   ├── crawlers/              # Web scraping TopGo.vn
│   ├── embeddings/            # Vector embeddings & search
│   ├── llm/                   # Ollama LLM client
│   └── rag/                   # RAG pipeline & prompts
│
├── docs/                      # 📚 Tài liệu
│   ├── DOCUMENTATION.md       # Tài liệu đầy đủ
│   ├── SETUP_OLLAMA.md        # Hướng dẫn cài Ollama
│   └── ...                    # Các tài liệu khác
│
├── scripts/                   # 🛠️ Utility scripts
│   ├── setup_ollama.bat       # Setup Ollama tự động
│   └── rebuild_embeddings.py  # Rebuild vector DB
│
├── app.py                     # 🎨 Streamlit UI (Main App)
├── start_all.bat              # 🚀 Khởi động tất cả services
├── stop_all.bat               # 🛑 Dừng tất cả services
├── requirements.txt           # 📦 Python dependencies
├── .env                       # ⚙️ Environment config
└── README.md                  # 📖 Bạn đang đọc file này
```

---

## 🎯 Sử dụng

### 1. Khởi động nhanh

```bash
# Windows: Double-click hoặc command line
.\start_all.bat

# Hoặc chạy trực tiếp
streamlit run app.py
```

### 2. Chat với AI

```
👤 Bạn: "Tìm nhà hàng Việt Nam bình dân ở Cầu Giấy"
🤖 AI: Dựa trên yêu cầu của bạn, tôi gợi ý:
     1. Quán Ăn Ngon - Cầu Giấy
        📍 123 Đường XYZ
        💰 Giá: 50k-100k/người
        ⭐ Phù hợp: 95%
```

**Chế độ hoạt động:**
- 🟢 **Ollama ON:** Full AI chat + semantic search
- 🟡 **Ollama OFF:** Chỉ semantic search (vẫn chính xác)

### 3. Filter tìm kiếm

- **Loại hình:** Nhà hàng, Bar, Karaoke
- **Quận:** Tây Hồ, Hoàn Kiếm, Cầu Giấy, Ba Đình...
- **Mức giá:** Bình dân, Trung bình, Cao cấp

---

## ⚙️ Kiến trúc (Đơn giản)

File `.env`:

```env
# Ollama Configuration (Local LLM)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2:1.5b
```

---

## 🛠️ Tech Stack

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

## 📊 Dữ liệu

- **1891 địa điểm** từ TopGo.vn
- **Loại hình:** Nhà hàng, Bar, Karaoke
- **Khu vực:** Hà Nội (các quận nội thành)
- **Thông tin:** Tên, địa chỉ, SĐT, giá, mô tả, đánh giá

---

## 🔧 Development

### Crawl dữ liệu mới

```bash
python src/crawlers/topgo_crawler.py
```

### Tạo lại embeddings

```bash
python scripts/rebuild_embeddings.py
```

### Xem thống kê project

```bash
python scripts/project_stats.py
```

### Chạy API Backend (Optional)

```bash
python scripts/run_api.py
# Hoặc: uvicorn src.api.main:app --reload
```

---

## 🐛 Troubleshooting

### 1. Lỗi "Ollama connection refused"

```bash
# Kiểm tra Ollama có chạy không
curl http://localhost:11434/api/tags

# Nếu không chạy, khởi động lại
ollama serve  # Linux/Mac
# Windows: Restart Ollama app
```

### 2. Model chưa có

```bash
ollama pull qwen2:1.5b
```

### 3. Port 8000 đã dùng

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

---

## � Tài liệu bổ sung

Xem thêm trong thư mục [docs/](docs/):

- 📘 [QUICKSTART_SIMPLE.md](docs/QUICKSTART_SIMPLE.md) - Quickstart 3 bước
- 🔧 [SETUP_OLLAMA.md](docs/SETUP_OLLAMA.md) - Setup Ollama chi tiết
- 🎨 [STREAMLIT_LOCAL.md](docs/STREAMLIT_LOCAL.md) - Hướng dẫn Streamlit
- ⚡ [OPTIMIZATION_DONE.md](docs/OPTIMIZATION_DONE.md) - Tối ưu đã làm
- 🔨 [RAG_IMPLEMENTATION.md](docs/RAG_IMPLEMENTATION.md) - RAG pipeline
- 📊 [API_BACKEND_COMPLETE.md](docs/API_BACKEND_COMPLETE.md) - API docs

---

## �📝 To-Do

- [ ] Add more filters (cuisine type, rating)
- [ ] Multi-language support
- [ ] User feedback system
- [ ] Recommendation history
- [ ] Mobile responsive UI

---

## 📄 License

MIT License

---

## 👥 Contributors

- Your Name - Initial work

---

## 🙏 Acknowledgments

- TopGo.vn - Data source
- Ollama - Local LLM framework
- ChromaDB - Vector database
- Sentence Transformers - Embeddings

---

## 📞 Support

- 📖 Docs: [SETUP_OLLAMA.md](SETUP_OLLAMA.md)
- 🐛 Issues: Create an issue on GitHub
- 💬 Discord: [Ollama Community](https://discord.gg/ollama)

# 🛠️ Utility Scripts

Thư mục này chứa các script tiện ích để quản lý project.

---

## 🚀 Khởi động

### `setup_ollama.bat` (Windows)
Kiểm tra và setup Ollama tự động.

```bash
./setup_ollama.bat
```

**Chức năng:**
- Kiểm tra Ollama đã cài chưa
- Kiểm tra model đã download chưa
- Hướng dẫn cài đặt nếu thiếu

---

## ▶️ Chạy ứng dụng

### `run_api.py`
Khởi động FastAPI backend server.

```bash
python scripts/run_api.py
```

**Port:** http://localhost:8000
**Docs:** http://localhost:8000/docs

### `run_streamlit.py`
Khởi động Streamlit UI.

```bash
python scripts/run_streamlit.py
```

**Port:** http://localhost:8501

---

## 📊 Data Processing

### `rebuild_embeddings.py`
Tạo lại vector embeddings từ dữ liệu raw.

```bash
python scripts/rebuild_embeddings.py
```

**Khi nào cần chạy:**
- Sau khi crawl dữ liệu mới
- Khi thay đổi embedding model
- Khi database bị lỗi

### `auto_process.py`
Tự động xử lý dữ liệu raw thành processed.

```bash
python scripts/auto_process.py
```

---

## 🕷️ Web Crawling

### `crawl_from_sitemap.py`
Crawl từ sitemap của TopGo.vn.

```bash
python scripts/crawl_from_sitemap.py
```

**Output:** `data/raw/restaurants.json`

---

## 📈 Monitoring & Stats

### `project_stats.py`
Xem thống kê project (files, lines, size).

```bash
python scripts/project_stats.py
```

**Output:**
```
📊 Project Statistics:
├── Total Files: 45
├── Total Lines: 3,245
├── Total Size: 2.5 MB
├── Python Files: 32
└── Documentation: 13
```

---

## 💡 Tips

### Chạy script từ root directory:
```bash
# Good ✅
python scripts/rebuild_embeddings.py

# Avoid ❌ (sẽ lỗi import path)
cd scripts && python rebuild_embeddings.py
```

### Debugging:
```bash
# Enable verbose logging
export LOG_LEVEL=DEBUG  # Linux/Mac
set LOG_LEVEL=DEBUG     # Windows

python scripts/your_script.py
```

---

## 🔄 Maintenance

### Định kỳ nên chạy:
- **Hàng tuần:** `crawl_from_sitemap.py` → `rebuild_embeddings.py`
- **Khi cần:** `project_stats.py` để kiểm tra size
- **Sau mỗi update:** `setup_ollama.bat` để verify config

---

## 📝 Notes

- Tất cả scripts đều giả định chạy từ **root directory** của project
- Cần activate Python environment trước khi chạy
- Xem log files trong `logs/` nếu có lỗi

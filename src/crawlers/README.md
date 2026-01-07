# 🕷️ Crawlers & Data Processing

Module này chứa code để crawl và xử lý dữ liệu từ TopGo.vn.

## 📁 Files

### Core Crawlers
- **`topgo_crawler.py`** - Main crawler lấy data từ TopGo.vn
  - Crawl từ category pages (nhà hàng, bar, karaoke)
  - Parse HTML để extract metadata
  - Lưu raw JSON

- **`data_processor.py`** - Xử lý và làm sạch dữ liệu
  - Normalize district names
  - Parse price ranges
  - Extract features và cuisine types
  - Tạo searchable text

- **`analyze_data.py`** - Phân tích và báo cáo thống kê
  - Count by district, type, price
  - Data quality checks
  - Missing data report

## 🚀 Usage

### 1. Crawl dữ liệu mới

```bash
# Crawl từ sitemap (recommended)
python scripts/crawl_from_sitemap.py

# Hoặc process từ raw data
python scripts/auto_process.py
```

### 2. Rebuild embeddings

```bash
python scripts/rebuild_embeddings.py
```

## 📊 Data Flow

```
TopGo.vn
    ↓ (topgo_crawler.py)
data/raw/restaurants_raw.json
    ↓ (data_processor.py)
data/processed/restaurants_clean.json
    ↓ (create_embeddings.py)
data/vector_db/ (ChromaDB)
    ↓
Search Engine → RAG Pipeline
```

## ⚠️ Important Notes

- **Production:** Crawler code không chạy trong production
- **Purpose:** Documentation và data updates
- **Data:** Current data đã được crawl (1891 địa điểm)
- **Updates:** Chạy crawler khi cần refresh data

## 🔧 Configuration

Edit trong `topgo_crawler.py`:
```python
max_pages_per_category = 50  # Limit pages per category
delay = 1  # Delay between requests (seconds)
```

## 📝 Data Structure

**Raw data:**
```json
{
  "name": "Nhà hàng ABC",
  "url": "https://topgo.vn/...",
  "description": "...",
  "phone": "0913515351",
  "address": "..."
}
```

**Processed data:**
```json
{
  "id": "rest_0001",
  "name": "Nhà hàng ABC",
  "district": "Hoàn Kiếm",
  "business_type": "restaurant",
  "price_range": "binh_dan",
  "cuisine_type": ["việt", "âu"],
  "features": ["gia_dinh", "sang_trong"],
  "searchable_text": "..."
}
```

## 🐛 Troubleshooting

**Crawler fails:**
- Check internet connection
- TopGo.vn might have changed HTML structure
- Add delay between requests

**Data quality issues:**
- Run `analyze_data.py` to check
- Manually fix in `restaurants_clean.json`
- Rebuild embeddings

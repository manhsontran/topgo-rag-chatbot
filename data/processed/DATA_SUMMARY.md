# 📊 Data Summary - TopGo RAG Chatbot

> **Cập nhật:** December 28, 2025

---

## 🎯 Tổng quan Dataset

| Metric | Giá trị |
|--------|---------|
| **Tổng địa điểm** | 1,891 |
| **Nguồn** | TopGo.vn (Hà Nội) |
| **Data file** | `restaurants_clean.json` |
| **Vector DB** | ChromaDB (1,891 embeddings) |

---

## 🏢 Phân bố theo Loại hình

| Loại hình | Số lượng | Tỷ lệ |
|-----------|----------|-------|
| Restaurant (Nhà hàng) | ~1,500 | ~79% |
| Bar/Pub | ~250 | ~13% |
| Karaoke | ~141 | ~8% |

---

## 📍 Phân bố theo Quận (Top 10)

| Quận | Số lượng | Ghi chú |
|------|----------|---------|
| Cầu Giấy | 968 | Nhiều nhất |
| Hoàn Kiếm | 541 | Khu trung tâm |
| Khác | 102 | Các quận ngoại thành |
| Đống Đa | 75 | |
| Ba Đình | 64 | |
| Hà Đông | 34 | |
| Hai Bà Trưng | 32 | |
| Tây Hồ | 29 | |
| Thanh Xuân | 23 | |
| Nam Từ Liêm | 12 | |
| Long Biên | 8 | |
| Bắc Từ Liêm | 3 | |

**Tổng: 33 quận được support** (bao gồm cả có dấu và không dấu)

---

## 💰 Phân bố theo Mức giá

| Mức giá | Mô tả | Tỷ lệ |
|---------|-------|-------|
| `binh_dan` | Dưới 200K/người | ~30% |
| `trung_binh` | 200K - 500K/người | ~45% |
| `cao_cap` | Trên 500K/người | ~25% |

---

## 🍽️ Loại ẩm thực

- Việt Nam
- Châu Âu (Âu)
- Nhật Bản
- Hàn Quốc
- Trung Quốc
- Fusion

---

## ⭐ Features (Đặc điểm)

| Feature | Mô tả |
|---------|-------|
| `sang_trong` | Không gian sang trọng |
| `gia_dinh` | Phù hợp gia đình |
| `hen_ho` | Phù hợp hẹn hò |
| `cong_ty` | Phù hợp tiệc công ty |
| `am_cung` | Không gian ấm cúng |
| `view_dep` | View đẹp |

---

## 📁 Data Structure

### Raw Data (`data/raw/`)
```
restaurants_raw.json    # Original crawled data (1,891 records, 7.5MB)
```

### Processed Data (`data/processed/`)
```
restaurants_clean.json  # Clean, structured data (1,891 records, 4MB)
```

### Vector Database (`data/vector_db/`)
```
chroma.sqlite3          # ChromaDB with embeddings
```

---

## 🔧 Data Schema

```json
{
  "id": "rest_0001",
  "name": "Nhà hàng ABC",
  "description": "Mô tả chi tiết...",
  "phone": "0913515351",
  "address": "123 Đường XYZ, Quận ABC, Hà Nội",
  "district": "Hoàn Kiếm",
  "business_type": "restaurant",
  "cuisine_type": ["việt", "âu"],
  "price_range": "binh_dan",
  "features": ["gia_dinh", "sang_trong"],
  "url": "https://topgo.vn/...",
  "searchable_text": "Tên: Nhà hàng ABC\nLoại hình: RESTAURANT..."
}
```

---

## ✅ Tính năng Data

### 1. Data Quality
- ✅ 1,891 địa điểm
- ✅ 100% có số điện thoại
- ✅ 100% có địa chỉ
- ✅ District được normalize và validate

### 2. Search & Filter
- ✅ Semantic search với embeddings (paraphrase-multilingual-MiniLM-L12-v2)
- ✅ Filter theo quận (33 quận Hà Nội)
- ✅ Filter theo loại hình (restaurant, bar, karaoke)
- ✅ Filter theo mức giá

### 3. Validation
- ✅ District validation (reject quận không hợp lệ)
- ✅ Price range normalization
- ✅ Business type categorization

---

## 🚀 Sử dụng

### Search trong code
```python
from src.embeddings.search_engine import RestaurantSearchEngine

engine = RestaurantSearchEngine()
results = engine.search(
    query="nhà hàng Việt Nam",
    n_results=5,
    filters={
        "district": "Hoàn Kiếm",
        "price_range": "binh_dan"
    }
)
```

### Rebuild embeddings
```bash
python scripts/rebuild_embeddings.py
```

---

## 📝 Notes

- Data được crawl từ TopGo.vn
- Chỉ bao gồm địa điểm tại **Hà Nội**
- Update định kỳ bằng cách chạy crawler
- Vector DB cần rebuild khi data thay đổi

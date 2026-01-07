# 🍽️ TopGo AI Chatbot - Streamlit Frontend

## ✅ Features

### Features:

#### 1. **💬 Chat with AI**
- Beautiful chat interface with message bubbles
- Real-time conversation with AI
- Display chat history
- Fully integrated RAG pipeline
- Vietnamese LLM responses (qwen2:1.5b)

#### 2. **🔍 Search**
- Semantic search with keywords
- Filters: type, district, price range
- Display similarity scores
- Sort by relevance

#### 3. **🎯 Personalized Recommendations**
- Occasion-based (dating, birthday, class reunion...)
- Group size consideration
- Budget filtering
- District preference

#### 4. **🎨 UI/UX**
- Modern, clean design
- Custom CSS styling
- Restaurant cards with complete information
- Price badges (cheap/moderate/expensive)
- Similarity scores
- Icons for each type
- Responsive layout
- Loading states
- Error handling

#### 5. **⚙️ Sidebar Controls**
- API health check
- Mode selection (Chat/Search/Recommend)
- Filters: type, district, price
- Settings: RAG on/off
- Clear chat history
- About section

#### 6. **📊 Features**
- Session state management
- Conversation history (last 10 messages)
- API integration with FastAPI backend
- Error handling & fallbacks
- Sample questions for quick start

## 🚀 How to Run

### Step 1: Install dependencies
```bash
pip install streamlit==1.28.1
```

Or:
```bash
pip install -r requirements.txt
```

### Step 2: Start API backend (terminal 1)
```bash
python run_api.py
```

### Step 3: Start Streamlit frontend (terminal 2)
```bash
streamlit run app.py
```

Or use the script:
```bash
python run_streamlit.py
```

### Step 4: Open browser
Access: **http://localhost:8501**

## 📸 Main Features

### Chat Mode
- Enter natural language questions in Vietnamese
- AI responds and suggests restaurants
- Display restaurant cards
- Chat history is saved

### Search Mode
- Search by keywords
- Apply filters
- View results with similarity scores

### Recommendation Mode
- Select occasion
- Enter number of people
- Set budget
- Choose area
- Receive AI recommendations

## 🎨 UI Components

### Restaurant Cards
Each card displays:
- ✅ Restaurant name + icon
- ✅ Full address
- ✅ District
- ✅ Price range (colored badge)
- ✅ Phone number
- ✅ Short description
- ✅ TopGo.vn link
- ✅ Similarity score

### Sidebar
- ✅ API health status
- ✅ Database stats
- ✅ LLM model info
- ✅ Mode selector
- ✅ Filters (type, district, price)
- ✅ Advanced settings
- ✅ Clear chat button

## 🔧 Configuration

API endpoint is configured in `app.py`:
```python
API_BASE_URL = "http://localhost:8000"
```

To change, edit this variable or create a `.env` file.

## ✨ Sample Questions

The app includes 4 sample questions:
1. 🍜 "Affordable Vietnamese restaurant in Cau Giay"
2. 🎤 "VIP Karaoke suitable for 30-person class reunion"
3. 🍺 "Bar with nice view in Tay Ho for dating"
4. 🍱 "Buffet suitable for family of 6"

## 📱 Responsive Design

- ✅ Desktop optimized
- ✅ Wide layout
- ✅ Expandable sidebar
- ✅ Mobile-friendly (Streamlit default)

## 🐛 Error Handling

- ✅ API connection errors
- ✅ Timeout handling
- ✅ Empty results
- ✅ Invalid inputs
- ✅ Health check failures

## 🎯 Next Steps (Optional)

1. **Deployment**: Deploy to Streamlit Cloud
2. **Authentication**: Add user login
3. **Favorites**: Save favorite restaurants
4. **Reviews**: User ratings & reviews
5. **Images**: Restaurant photos
6. **Maps**: Google Maps integration
7. **Booking**: Table reservation
8. **Multi-language**: English support

## 📊 Tech Stack

- **Frontend**: Streamlit 1.28.1
- **Backend API**: FastAPI
- **LLM**: Ollama (qwen2:1.5b)
- **Search**: ChromaDB + sentence-transformers
- **Data**: 1,891 restaurants from TopGo.vn

## ✅ Features Summary

- ✅ 3 modes (Chat, Search, Recommend)
- ✅ Beautiful UI with custom CSS
- ✅ Full API integration
- ✅ Error handling
- ✅ Responsive design
- ✅ Session state management

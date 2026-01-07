# FastAPI Backend - TopGo RAG Chatbot

## ✅ Features

### 1. API Models (`src/api/models.py`)
- ✅ Pydantic schemas for request/response validation
- ✅ ChatRequest, ChatResponse
- ✅ SearchRequest, SearchResponse  
- ✅ RecommendationRequest, RecommendationResponse
- ✅ HealthResponse, ErrorResponse
- ✅ Enums: RestaurantType, PriceRange

### 2. Main FastAPI Application (`src/api/main.py`)
- ✅ FastAPI app with CORS middleware
- ✅ Automatic Swagger UI documentation (`/docs`)
- ✅ ReDoc documentation (`/redoc`)
- ✅ Startup/shutdown events
- ✅ Global state management
- ✅ Exception handlers

### 3. Endpoints Implemented

#### Health Endpoints
- `GET /` - Root endpoint with API info
- `GET /health` - Health check with database and LLM status

#### Chat Endpoint
- `POST /api/chat` - Chat with AI chatbot
  - Full RAG mode (retrieval + generation)
  - Search-only mode
  - Conversation history support
  - Filters: type, district, price

#### Search Endpoint
- `POST /api/search` - Semantic search
  - Top-k results
  - Multiple filters
  - Minimum similarity score
  - Sorted by relevance

#### Recommendations Endpoint
- `POST /api/recommendations` - Personalized recommendations
  - Occasion-based (birthday, date, meeting)
  - Group size consideration
  - Budget filtering
  - District preference
  - Custom preferences

### 4. Features

#### Automatic Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Interactive API testing
- Request/response examples
- Schema validation

#### Error Handling
- HTTP exception handler
- General exception handler  
- Detailed error messages
- Error logging

#### Startup Checks
- Vector database connection
- Ollama LLM availability
- Model listing
- Graceful degradation (search-only if LLM unavailable)

### 5. Integration

✅ **Vector Database**: ChromaDB with 159 restaurants
✅ **Embeddings**: sentence-transformers multilingual model
✅ **LLM**: Ollama with qwen2:7b (Vietnamese-optimized)
✅ **RAG Pipeline**: Full retrieval + generation
✅ **Search Engine**: Semantic search with filters

### 6. Startup Script

`run_api.py` - Quick start script:
```bash
python run_api.py
```

Server configuration:
- Host: 0.0.0.0
- Port: 8000
- Reload: True (development mode)
- Log level: INFO

### 7. Testing

Created `test_api.py` with 8 test cases:
1. Root endpoint
2. Health check
3. Chat with RAG
4. Chat search-only
5. Semantic search
6. Search with filters
7. Recommendations (romantic dinner)
8. Recommendations (birthday)

## How to Use

### Start API Server
```bash
python run_api.py
```

### Access Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Example Requests

#### Chat with AI
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Find affordable Vietnamese restaurants in Cau Giay",
    "use_rag": true,
    "top_k": 5
  }'
```

#### Search
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "spicy Thai hotpot",
    "top_k": 10,
    "restaurant_type": "restaurant",
    "min_score": 0.5
  }'
```

#### Recommendations
```bash
curl -X POST http://localhost:8000/api/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "occasion": "dating",
    "group_size": 2,
    "budget_per_person": 500000,
    "district": "Tay Ho"
  }'
```

### Test All Endpoints
```bash
python test_api.py
```

## API Response Examples

### Chat Response
```json
{
  "answer": "Hello! I found 3 affordable Vietnamese restaurants in Cau Giay...",
  "restaurants": [
    {
      "name": "Vietnamese Heritage Cuisine",
      "type": "restaurant",
      "address": "123 Duong Lang, Dong Da, Ha Noi",
      "district": "Dong Da",
      "price_range": "moderate",
      "similarity_score": 0.85
    }
  ],
  "sources_count": 3,
  "query_type": "rag",
  "llm_model": "qwen2:7b"
}
```

### Health Response
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database_status": "connected",
  "llm_status": "connected",
  "total_restaurants": 1891,
  "available_models": ["qwen2:1.5b"]
}
```

## ✅ Backend Features

- All endpoints implemented
- Full RAG integration
- Vietnamese LLM responses
- Automatic documentation
- Error handling
- Health checks
- CORS configured
- Logging enabled
- Graceful error handling
- API versioning ready

## Next Steps

1. **Frontend Development**: Create web UI with React/Vue/Streamlit
2. **Authentication**: Add user authentication & API keys
3. **Rate Limiting**: Implement request rate limiting
4. **Caching**: Add Redis caching for common queries
5. **Monitoring**: Setup monitoring & analytics
6. **Deployment**: Deploy to cloud (AWS/GCP/Azure)

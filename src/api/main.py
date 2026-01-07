"""
FastAPI Main Application - REST API for TopGo RAG Chatbot
"""
import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from project root
load_dotenv(dotenv_path=project_root / '.env')

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from src.api.models import (
    ChatRequest, ChatResponse, RestaurantInfo,
    SearchRequest, SearchResponse,
    RecommendationRequest, RecommendationResponse,
    HealthResponse, ErrorResponse,
    RestaurantType, PriceRange
)
from src.rag.pipeline import RAGPipeline
from src.embeddings.search_engine import RestaurantSearchEngine
from src.llm.ollama_client import OllamaClient

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== FASTAPI APP SETUP ==========

app = FastAPI(
    title="TopGo RAG Chatbot API",
    description="TopGo RAG Chatbot API - He thong goi y nha hang thong minh voi AI. Chat voi AI, tim kiem semantic, goi y ca nhan hoa. Du lieu: 159 nha hang tu TopGo.vn (Ha Noi). LLM: qwen2:7b (Vietnamese-optimized)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "chat",
            "description": "💬 Chat endpoints - Trò chuyện với AI chatbot"
        },
        {
            "name": "search",
            "description": "🔍 Search endpoints - Tìm kiếm nhà hàng"
        },
        {
            "name": "recommendations",
            "description": "🎯 Recommendation endpoints - Gợi ý nhà hàng"
        },
        {
            "name": "health",
            "description": "❤️ Health endpoints - Kiểm tra hệ thống"
        }
    ]
)

# ========== CORS MIDDLEWARE ==========

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== GLOBAL STATE ==========

class AppState:
    """Global application state"""
    rag_pipeline: Optional[RAGPipeline] = None
    search_engine: Optional[RestaurantSearchEngine] = None
    ollama_client: Optional[OllamaClient] = None
    is_initialized: bool = False
    error_message: Optional[str] = None

state = AppState()

# ========== STARTUP & SHUTDOWN EVENTS ==========

@app.on_event("startup")
async def startup_event():
    """Initialize RAG pipeline and components on startup"""
    logger.info("🚀 Starting TopGo RAG Chatbot API...")
    
    try:
        # Initialize search engine
        logger.info("📚 Loading vector database...")
        state.search_engine = RestaurantSearchEngine()
        logger.info(f"✅ Search engine loaded with {state.search_engine.collection.count()} restaurants")
        
        # Initialize RAG pipeline with Ollama (Local LLM)
        logger.info("🔧 Initializing RAG pipeline...")
        logger.info("🤖 Using Ollama (Local LLM - Free, No API Keys Required)")
        
        state.rag_pipeline = RAGPipeline(
            model="qwen2:1.5b",  # Fast, Vietnamese-optimized
            ollama_url="http://localhost:11434",
            search_top_k=5
        )
        logger.info("✅ RAG pipeline initialized")
        
        state.is_initialized = True
        logger.info("✅ API startup complete - Ready to serve requests!")
        
    except Exception as e:
        logger.error(f"❌ Error during startup: {str(e)}")
        state.error_message = str(e)
        state.is_initialized = False
        # Don't raise - allow API to start in degraded mode


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Shutting down TopGo RAG Chatbot API...")
    state.is_initialized = False


# ========== EXCEPTION HANDLERS ==========

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.detail,
            "details": None
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "Đã xảy ra lỗi không mong muốn. Vui lòng thử lại sau.",
            "details": {"exception": str(exc)}
        }
    )


# ========== HELPER FUNCTIONS ==========

def check_initialized():
    """Check if the app is properly initialized"""
    if not state.is_initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Hệ thống chưa sẵn sàng. Lỗi: {state.error_message or 'Unknown error'}"
        )


def format_restaurant_info(result: Dict[str, Any]) -> RestaurantInfo:
    """Convert search result to RestaurantInfo model"""
    return RestaurantInfo(
        name=result.get('name', 'Unknown'),
        type=result.get('type', 'other'),
        address=result.get('address', ''),
        district=result.get('district', ''),
        price_range=result.get('price_range', 'moderate'),
        phone=result.get('phone'),
        description=result.get('description'),
        url=result.get('url'),
        similarity_score=result.get('similarity_score')
    )


# ========== HEALTH ENDPOINTS ==========

@app.get("/", tags=["health"])
async def root():
    """Root endpoint - API info"""
    return {
        "message": "TopGo RAG Chatbot API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """
    Kiểm tra trạng thái hệ thống
    
    Returns:
        - Trạng thái API, database, LLM
        - Số lượng nhà hàng
        - Danh sách models có sẵn
    """
    try:
        # Check database
        db_status = "disconnected"
        total_restaurants = 0
        if state.search_engine:
            try:
                total_restaurants = state.search_engine.collection.count()
                db_status = "connected"
            except Exception as e:
                logger.error(f"Database check failed: {e}")
                db_status = "error"
        
        # Check LLM
        llm_status = "disconnected"
        available_models = []
        if state.ollama_client:
            try:
                if state.ollama_client.check_connection():
                    llm_status = "connected"
                    available_models = state.ollama_client.list_models()
            except Exception as e:
                logger.error(f"LLM check failed: {e}")
                llm_status = "error"
        
        # Overall status
        overall_status = "healthy" if state.is_initialized else "degraded"
        
        return HealthResponse(
            status=overall_status,
            version="1.0.0",
            database_status=db_status,
            llm_status=llm_status,
            total_restaurants=total_restaurants,
            available_models=available_models
        )
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


# ========== CHAT ENDPOINTS ==========

@app.post("/api/chat", response_model=ChatResponse, tags=["chat"])
async def chat(request: ChatRequest):
    """
    💬 Chat với AI chatbot
    
    Gửi câu hỏi bằng tiếng Việt và nhận câu trả lời từ AI kèm danh sách nhà hàng phù hợp.
    
    **Modes:**
    - `use_rag=True`: Full RAG (Retrieval + AI Generation) - Câu trả lời tự nhiên
    - `use_rag=False`: Search only - Chỉ tìm kiếm và liệt kê
    
    **Filters:**
    - `type`: restaurant/bar/karaoke/cafe
    - `district`: Cau Giay/Dong Da/Hoan Kiem/etc
    - `price`: cheap/moderate/expensive
    
    **Examples:**
    - "Tìm quán bar có view đẹp ở Tây Hồ"
    - "Nhà hàng Việt Nam bình dân cho sinh viên"
    - "Karaoke sang trọng phù hợp họp lớp"
    """
    check_initialized()
    
    try:
        logger.info(f"Chat request: {request.query[:100]}...")
        
        # Call RAG pipeline - answer() tự động classify query
        if request.use_rag:
            # Full RAG mode với LLM classification
            if not state.rag_pipeline:
                raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
            result = state.rag_pipeline.answer(
                query=request.query,
                top_k=request.top_k,
                filters=request.filters
            )
            
            query_type = "rag"
            answer = result['answer']
            llm_model = state.rag_pipeline.model if state.rag_pipeline else 'gemini-2.0-flash'
            
        else:
            # Search-only mode (no LLM)
            if not state.rag_pipeline:
                raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
            results = state.rag_pipeline.retrieve(
                query=request.query,
                top_k=request.top_k,
                filters=request.filters
            )
            
            query_type = "search"
            llm_model = None
            
            # Format simple answer
            if results:
                answer = f"Tìm thấy {len(results)} nhà hàng phù hợp với yêu cầu của bạn:\n\n"
                for i, r in enumerate(results, 1):
                    answer += f"{i}. **{r['name']}** - {r['address']}\n"
                    if r.get('description'):
                        answer += f"   {r['description'][:100]}...\n"
            else:
                answer = "Xin lỗi, không tìm thấy nhà hàng phù hợp với yêu cầu của bạn."
            
            result = {'sources': results}
        
        # Format restaurants
        restaurants = [
            format_restaurant_info(r) 
            for r in result.get('sources', [])
        ]
        
        return ChatResponse(
            answer=answer,
            restaurants=restaurants,
            sources_count=len(restaurants),
            query_type=query_type,
            llm_model=llm_model
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xử lý chat: {str(e)}"
        )


# ========== SEARCH ENDPOINTS ==========

@app.post("/api/search", response_model=SearchResponse, tags=["search"])
async def search(request: SearchRequest):
    """
    🔍 Tìm kiếm nhà hàng
    
    Semantic search với bộ lọc chi tiết.
    
    **Parameters:**
    - `query`: Từ khóa tìm kiếm (VD: "lẩu Thái", "view hồ Tây")
    - `top_k`: Số lượng kết quả (1-50)
    - `restaurant_type`: Loại hình (restaurant/bar/karaoke/cafe)
    - `district`: Quận/huyện
    - `price_range`: Khoảng giá (cheap/moderate/expensive)
    - `min_score`: Điểm tương đồng tối thiểu (0-1)
    
    **Returns:**
    - Danh sách nhà hàng được sắp xếp theo độ phù hợp
    """
    check_initialized()
    
    try:
        logger.info(f"Search request: {request.query}")
        
        # Build filters
        filters = {}
        if request.restaurant_type:
            filters['type'] = request.restaurant_type.value
        if request.district:
            filters['district'] = request.district
        if request.price_range and request.price_range != PriceRange.all:
            filters['price'] = request.price_range.value
        
        # Search
        if not state.search_engine:
            raise HTTPException(status_code=503, detail="Search engine not initialized")
        results = state.search_engine.search(
            query=request.query,
            n_results=request.top_k,
            filters=filters if filters else None
        )
        
        # Filter by minimum score
        filtered_results = [
            r for r in results 
            if r.get('similarity_score', 0) >= request.min_score
        ]
        
        # Format results
        restaurants = [format_restaurant_info(r) for r in filtered_results]
        
        return SearchResponse(
            query=request.query,
            restaurants=restaurants,
            total_found=len(restaurants),
            filters_applied=filters
        )
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tìm kiếm: {str(e)}"
        )


# ========== RECOMMENDATION ENDPOINTS ==========

@app.post("/api/recommendations", response_model=RecommendationResponse, tags=["recommendations"])
async def get_recommendations(request: RecommendationRequest):
    """
    🎯 Nhận gợi ý nhà hàng cá nhân hóa
    
    Dựa trên dịp, số người, ngân sách và sở thích để gợi ý nhà hàng phù hợp.
    
    **Parameters:**
    - `occasion`: Dịp (sinh nhật, hẹn hò, họp lớp, gia đình, công ty, etc)
    - `group_size`: Số người
    - `budget_per_person`: Ngân sách/người (VND)
    - `district`: Khu vực ưu tiên
    - `preferences`: Sở thích (view đẹp, yên tĩnh, parking, etc)
    
    **Examples:**
    ```json
    {
        "occasion": "hẹn hò",
        "group_size": 2,
        "budget_per_person": 500000,
        "district": "Tay Ho",
        "preferences": ["view hồ Tây", "lãng mạn"]
    }
    ```
    """
    check_initialized()
    
    try:
        logger.info(f"Recommendation request: {request.occasion}, {request.group_size} people")
        
        # Build query from criteria
        query_parts = []
        
        if request.occasion:
            occasion_keywords = {
                "sinh nhật": "phù hợp sinh nhật, không gian vui vẻ",
                "hẹn hò": "lãng mạn, view đẹp, riêng tư",
                "họp lớp": "phòng riêng, karaoke, nhóm đông",
                "gia đình": "gia đình, trẻ em, thoải mái",
                "công ty": "chuyên nghiệp, phòng VIP, hội nghị"
            }
            query_parts.append(occasion_keywords.get(request.occasion.lower(), request.occasion))
        
        if request.preferences:
            query_parts.extend(request.preferences)
        
        query = " ".join(query_parts) if query_parts else "nhà hàng tốt"
        
        # Determine filters
        filters = {}
        
        # Price filter based on budget
        if request.budget_per_person:
            if request.budget_per_person < 100000:
                filters['price'] = 'cheap'
            elif request.budget_per_person < 300000:
                filters['price'] = 'moderate'
            else:
                filters['price'] = 'expensive'
        
        if request.district:
            filters['district'] = request.district
        
        # Determine restaurant type from occasion
        if request.occasion and "karaoke" in request.occasion.lower():
            filters['type'] = 'karaoke'
        elif request.occasion and any(kw in request.occasion.lower() for kw in ["bar", "rượu", "cocktail"]):
            filters['type'] = 'bar'
        
        # Search
        if not state.search_engine:
            raise HTTPException(status_code=503, detail="Search engine not initialized")
        n_results = min(request.group_size, 10) if request.group_size else 5
        results = state.search_engine.search(
            query=query,
            n_results=n_results,
            filters=filters if filters else None
        )
        
        # Format results
        recommendations = [format_restaurant_info(r) for r in results]
        
        # Generate suggestion reason
        reason_parts = []
        if request.occasion:
            reason_parts.append(f"phù hợp cho {request.occasion}")
        if request.group_size:
            reason_parts.append(f"{request.group_size} người")
        if request.budget_per_person:
            budget_text = f"{request.budget_per_person:,}đ/người"
            reason_parts.append(f"ngân sách {budget_text}")
        if request.district:
            reason_parts.append(f"tại {request.district}")
        
        suggestion_reason = "Các nhà hàng này " + ", ".join(reason_parts) if reason_parts else "Gợi ý nhà hàng phù hợp"
        
        return RecommendationResponse(
            recommendations=recommendations,
            criteria_used={
                "occasion": request.occasion,
                "group_size": request.group_size,
                "budget_per_person": request.budget_per_person,
                "district": request.district,
                "preferences": request.preferences
            },
            suggestion_reason=suggestion_reason,
            total_recommendations=len(recommendations)
        )
        
    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo gợi ý: {str(e)}"
        )


# ========== RUN SERVER ==========

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

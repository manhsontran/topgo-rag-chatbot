"""
API Models - Pydantic schemas for request/response validation
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class RestaurantType(str, Enum):
    """Loại hình nhà hàng"""
    restaurant = "restaurant"
    bar = "bar"
    karaoke = "karaoke"
    cafe = "cafe"
    buffet = "buffet"
    other = "other"


class PriceRange(str, Enum):
    """Khoảng giá"""
    cheap = "cheap"           # < 100k/người
    moderate = "moderate"     # 100k-300k/người
    expensive = "expensive"   # > 300k/người
    all = "all"


# ========== CHAT ENDPOINTS ==========

class ChatRequest(BaseModel):
    """Request cho chat endpoint"""
    query: str = Field(..., description="Câu hỏi của người dùng (tiếng Việt)", min_length=1)
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Lịch sử hội thoại trước đó [{'role': 'user'/'assistant', 'content': '...'}]"
    )
    use_rag: bool = Field(
        default=True,
        description="Sử dụng RAG (retrieval + generation) hay chỉ search"
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Số lượng kết quả tìm kiếm tối đa"
    )
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Bộ lọc tìm kiếm {'type': 'restaurant', 'district': 'Cau Giay', 'price': 'cheap'}"
    )
    
    model_config = ConfigDict(json_schema_extra={
            "example": {
                "query": "Tìm nhà hàng Việt Nam bình dân ở Cầu Giấy",
                "use_rag": True,
                "top_k": 5,
                "filters": {
                    "type": "restaurant",
                    "district": "Cau Giay",
                    "price": "cheap"
                }
            }
        })


class RestaurantInfo(BaseModel):
    """Thông tin nhà hàng"""
    name: str = Field(..., description="Tên nhà hàng")
    type: str = Field(..., description="Loại hình (restaurant/bar/karaoke/cafe)")
    address: str = Field(..., description="Địa chỉ đầy đủ")
    district: str = Field(..., description="Quận/huyện")
    price_range: str = Field(..., description="Khoảng giá (cheap/moderate/expensive)")
    phone: Optional[str] = Field(None, description="Số điện thoại")
    description: Optional[str] = Field(None, description="Mô tả chi tiết")
    url: Optional[str] = Field(None, description="Link TopGo")
    similarity_score: Optional[float] = Field(None, description="Điểm tương đồng (0-1)")
    
    model_config = ConfigDict(json_schema_extra={
            "example": {
                "name": "Cơm Việt Heritage",
                "type": "restaurant",
                "address": "123 Đường Láng, Đống Đa, Hà Nội",
                "district": "Dong Da",
                "price_range": "moderate",
                "phone": "024 1234 5678",
                "description": "Nhà hàng Việt Nam truyền thống...",
                "url": "https://topgo.vn/com-viet-heritage",
                "similarity_score": 0.85
            }
        })


class ChatResponse(BaseModel):
    """Response cho chat endpoint"""
    model_config = {"protected_namespaces": ()}
    
    answer: str = Field(..., description="Câu trả lời từ AI (tiếng Việt)")
    restaurants: List[RestaurantInfo] = Field(
        default=[],
        description="Danh sách nhà hàng được tìm thấy"
    )
    sources_count: int = Field(..., description="Số lượng nguồn được sử dụng")
    query_type: str = Field(..., description="Loại query: 'search' hoặc 'rag'")
    llm_model: Optional[str] = Field(None, description="Model LLM được sử dụng")
    
    model_config = ConfigDict(json_schema_extra={
            "example": {
                "answer": "Chào bạn! Tôi đã tìm thấy 3 nhà hàng Việt Nam bình dân ở Cầu Giấy...",
                "restaurants": [
                    {
                        "name": "Cơm Việt Heritage",
                        "type": "restaurant",
                        "address": "123 Đường Láng, Đống Đa, Hà Nội",
                        "district": "Dong Da",
                        "price_range": "moderate",
                        "similarity_score": 0.85
                    }
                ],
                "sources_count": 3,
                "query_type": "rag",
                "llm_model": "qwen2:7b"
            }
        })


# ========== SEARCH ENDPOINTS ==========

class SearchRequest(BaseModel):
    """Request cho search endpoint"""
    query: str = Field(..., description="Từ khóa tìm kiếm (tiếng Việt)", min_length=1)
    top_k: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Số lượng kết quả tối đa"
    )
    restaurant_type: Optional[RestaurantType] = Field(
        default=None,
        description="Lọc theo loại hình"
    )
    district: Optional[str] = Field(
        default=None,
        description="Lọc theo quận/huyện (VD: 'Cau Giay', 'Dong Da')"
    )
    price_range: Optional[PriceRange] = Field(
        default=None,
        description="Lọc theo khoảng giá"
    )
    min_score: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Điểm tương đồng tối thiểu (0-1)"
    )
    
    model_config = ConfigDict(json_schema_extra={
            "example": {
                "query": "lẩu Thái cay",
                "top_k": 10,
                "restaurant_type": "restaurant",
                "district": "Hoan Kiem",
                "price_range": "moderate",
                "min_score": 0.5
            }
        })


class SearchResponse(BaseModel):
    """Response cho search endpoint"""
    query: str = Field(..., description="Câu truy vấn gốc")
    restaurants: List[RestaurantInfo] = Field(..., description="Kết quả tìm kiếm")
    total_found: int = Field(..., description="Tổng số kết quả")
    filters_applied: Dict[str, Any] = Field(..., description="Bộ lọc đã áp dụng")
    
    model_config = ConfigDict(json_schema_extra={
            "example": {
                "query": "lẩu Thái cay",
                "restaurants": [],
                "total_found": 5,
                "filters_applied": {
                    "type": "restaurant",
                    "district": "Hoan Kiem",
                    "price": "moderate"
                }
            }
        })


# ========== RECOMMENDATIONS ENDPOINTS ==========

class RecommendationRequest(BaseModel):
    """Request cho recommendations endpoint"""
    occasion: Optional[str] = Field(
        default=None,
        description="Dịp đặc biệt (VD: 'sinh nhật', 'hẹn hò', 'họp lớp')"
    )
    group_size: Optional[int] = Field(
        default=None,
        ge=1,
        le=100,
        description="Số lượng người"
    )
    budget_per_person: Optional[int] = Field(
        default=None,
        ge=0,
        description="Ngân sách/người (VND)"
    )
    district: Optional[str] = Field(
        default=None,
        description="Quận/huyện ưu tiên"
    )
    preferences: Optional[List[str]] = Field(
        default=None,
        description="Sở thích (VD: ['view đẹp', 'không gian yên tĩnh', 'có parking'])"
    )
    
    model_config = ConfigDict(json_schema_extra={
            "example": {
                "occasion": "hẹn hò",
                "group_size": 2,
                "budget_per_person": 300000,
                "district": "Tay Ho",
                "preferences": ["view hồ Tây", "không gian lãng mạn"]
            }
        })


class RecommendationResponse(BaseModel):
    """Response cho recommendations endpoint"""
    recommendations: List[RestaurantInfo] = Field(..., description="Danh sách gợi ý")
    criteria_used: Dict[str, Any] = Field(..., description="Tiêu chí đã sử dụng")
    suggestion_reason: str = Field(..., description="Lý do gợi ý (tiếng Việt)")
    total_recommendations: int = Field(..., description="Số lượng gợi ý")
    
    model_config = ConfigDict(json_schema_extra={
            "example": {
                "recommendations": [],
                "criteria_used": {
                    "occasion": "hẹn hò",
                    "group_size": 2,
                    "budget": 300000,
                    "district": "Tay Ho"
                },
                "suggestion_reason": "Các nhà hàng này phù hợp cho hẹn hò với view hồ Tây đẹp",
                "total_recommendations": 3
            }
        })


# ========== HEALTH & INFO ENDPOINTS ==========

class HealthResponse(BaseModel):
    """Response cho health check endpoint"""
    status: str = Field(..., description="Trạng thái hệ thống")
    version: str = Field(..., description="Phiên bản API")
    database_status: str = Field(..., description="Trạng thái vector database")
    llm_status: str = Field(..., description="Trạng thái LLM (Ollama)")
    total_restaurants: int = Field(..., description="Tổng số nhà hàng trong database")
    available_models: List[str] = Field(..., description="Danh sách models có sẵn")
    
    model_config = ConfigDict(json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "database_status": "connected",
                "llm_status": "connected",
                "total_restaurants": 159,
                "available_models": ["qwen2:7b", "llama2:latest"]
            }
        })


class ErrorResponse(BaseModel):
    """Response khi có lỗi"""
    error: str = Field(..., description="Loại lỗi")
    message: str = Field(..., description="Thông báo lỗi chi tiết")
    details: Optional[Dict[str, Any]] = Field(None, description="Chi tiết bổ sung")
    
    model_config = ConfigDict(json_schema_extra={
            "example": {
                "error": "ValidationError",
                "message": "Query không được để trống",
                "details": {"field": "query", "constraint": "min_length"}
            }
        })

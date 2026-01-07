"""
TopGo RAG Chatbot - Streamlit Frontend
Giao diện chat thông minh cho gợi ý nhà hàng với AI
"""
import streamlit as st
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime

# ========== PAGE CONFIG ==========

st.set_page_config(
    page_title="TopGo AI Chatbot - Gợi ý nhà hàng thông minh",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CUSTOM CSS ==========

st.markdown("""
<style>
    /* Main styling */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Chat messages */
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        margin-left: 20%;
        text-align: right;
    }
    
    .assistant-message {
        background-color: #ffffff;
        color: #333;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        margin-right: 20%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Restaurant cards */
    .restaurant-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #007bff;
    }
    
    .restaurant-name {
        font-size: 20px;
        font-weight: bold;
        color: #007bff;
        margin-bottom: 8px;
    }
    
    .restaurant-info {
        color: #666;
        margin: 5px 0;
    }
    
    .restaurant-description {
        color: #333;
        margin-top: 10px;
        font-style: italic;
    }
    
    .price-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        margin-right: 10px;
    }
    
    .price-cheap {
        background-color: #28a745;
        color: white;
    }
    
    .price-moderate {
        background-color: #ffc107;
        color: #333;
    }
    
    .price-expensive {
        background-color: #dc3545;
        color: white;
    }
    
    .similarity-score {
        float: right;
        color: #007bff;
        font-weight: bold;
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    /* Stats */
    .stat-card {
        background: white;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .stat-number {
        font-size: 32px;
        font-weight: bold;
        color: #007bff;
    }
    
    .stat-label {
        color: #666;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ========== API CONFIG ==========

API_BASE_URL = "http://localhost:8000"

# ========== SESSION STATE ==========

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'restaurants' not in st.session_state:
    st.session_state.restaurants = []

if 'api_healthy' not in st.session_state:
    st.session_state.api_healthy = False

# ========== HELPER FUNCTIONS ==========

def check_api_health() -> Dict:
    """Check API health status"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            st.session_state.api_healthy = True
            return response.json()
        else:
            st.session_state.api_healthy = False
            return {"status": "unhealthy"}
    except Exception as e:
        st.session_state.api_healthy = False
        return {"status": "error", "error": str(e)}


def chat_with_ai(query: str, filters: Optional[Dict] = None, use_rag: bool = True) -> Dict:
    """Send chat request to API"""
    try:
        payload = {
            "query": query,
            "use_rag": use_rag,
            "top_k": 5,
            "conversation_history": st.session_state.conversation_history[-10:]  # Last 10 messages
        }
        
        if filters:
            payload["filters"] = filters
        
        response = requests.post(
            f"{API_BASE_URL}/api/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "answer": f"❌ Lỗi: {response.status_code} - {response.text}",
                "restaurants": [],
                "sources_count": 0,
                "query_type": "error"
            }
    except Exception as e:
        return {
            "answer": f"❌ Không thể kết nối với API: {str(e)}",
            "restaurants": [],
            "sources_count": 0,
            "query_type": "error"
        }


def search_restaurants(query: str, filters: Dict) -> Dict:
    """Search for restaurants"""
    try:
        payload = {
            "query": query,
            "top_k": 10,
            "min_score": 0.3
        }
        
        if filters.get('restaurant_type'):
            payload['restaurant_type'] = filters['restaurant_type']
        if filters.get('district'):
            payload['district'] = filters['district']
        if filters.get('price_range'):
            payload['price_range'] = filters['price_range']
        
        response = requests.post(
            f"{API_BASE_URL}/api/search",
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"restaurants": [], "total_found": 0}
    except Exception as e:
        st.error(f"Lỗi tìm kiếm: {str(e)}")
        return {"restaurants": [], "total_found": 0}


def get_recommendations(occasion: str, group_size: int, budget: int, district: str) -> Dict:
    """Get personalized recommendations"""
    try:
        payload = {
            "occasion": occasion,
            "group_size": group_size,
            "budget_per_person": budget
        }
        
        if district:
            payload["district"] = district
        
        response = requests.post(
            f"{API_BASE_URL}/api/recommendations",
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"recommendations": [], "total_recommendations": 0}
    except Exception as e:
        st.error(f"Lỗi gợi ý: {str(e)}")
        return {"recommendations": [], "total_recommendations": 0}


def display_restaurant_card(restaurant: Dict, index: int):
    """Display a restaurant card"""
    # Price badge color
    price_class = {
        'cheap': 'price-cheap',
        'moderate': 'price-moderate',
        'expensive': 'price-expensive'
    }.get(restaurant.get('price_range', 'moderate'), 'price-moderate')
    
    # Price text
    price_text = {
        'cheap': '💰 Bình dân',
        'moderate': '💰💰 Trung bình',
        'expensive': '💰💰💰 Cao cấp'
    }.get(restaurant.get('price_range', 'moderate'), '💰💰 Trung bình')
    
    # Similarity score
    score = restaurant.get('similarity_score', 0)
    score_display = f"{score:.1%}" if score else ""
    
    # Restaurant type icon
    type_icon = {
        'restaurant': '🍽️',
        'bar': '🍺',
        'karaoke': '🎤',
        'cafe': '☕',
        'buffet': '🍱'
    }.get(restaurant.get('type', 'restaurant'), '🍽️')
    
    st.markdown(f"""
    <div class="restaurant-card">
        <div class="restaurant-name">
            {type_icon} {restaurant.get('name', 'Unknown')}
            {f'<span class="similarity-score">Phù hợp: {score_display}</span>' if score_display else ''}
        </div>
        <div class="restaurant-info">
            📍 <strong>{restaurant.get('address', 'N/A')}</strong>
        </div>
        <div class="restaurant-info">
            🏙️ Quản: {restaurant.get('district', 'N/A')}
            &nbsp;&nbsp;|&nbsp;&nbsp;
            <span class="price-badge {price_class}">{price_text}</span>
        </div>
        {f'<div class="restaurant-info">📞 {restaurant.get("phone")}</div>' if restaurant.get('phone') else ''}
        {f'<div class="restaurant-description">"{str(restaurant.get("description", ""))[:200]}..."</div>' if restaurant.get('description') else ''}
    </div>
    """, unsafe_allow_html=True)
    
    # Display clickable link as button
    if restaurant.get('url'):
        st.link_button(
            "🔗 Xem chi tiết trên TopGo.vn",
            restaurant['url'],
            use_container_width=True
        )


# ========== SIDEBAR ==========

with st.sidebar:
    st.markdown("### ⚙️ Cài đặt")
    
    # API Health check
    health = check_api_health()
    
    if st.session_state.api_healthy:
        st.success("✅ API đang hoạt động")
        if 'total_restaurants' in health:
            st.info(f"📊 {health['total_restaurants']} nhà hàng trong database")
        if 'available_models' in health:
            st.info(f"🤖 LLM: {', '.join(health['available_models'])}")
    else:
        st.error("❌ API không khả dụng")
        st.warning("Vui lòng chạy: `python run_api.py`")
    
    st.markdown("---")
    
    # Mode selection
    st.markdown("### 🎯 Chế độ")
    mode = st.radio(
        "Chọn chế độ sử dụng:",
        ["💬 Chat với AI", "🔍 Tìm kiếm", "🎯 Gợi ý"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Filters
    st.markdown("### 🔧 Bộ lọc")
    
    restaurant_type = st.selectbox(
        "Loại hình:",
        ["Tất cả", "Nhà hàng", "Bar", "Karaoke", "Café", "Buffet"]
    )
    
    district = st.selectbox(
        "Quận/Huyện:",
        ["Tất cả", "Ba Dinh", "Hoan Kiem", "Dong Da", "Hai Ba Trung", 
         "Cau Giay", "Tay Ho", "Thanh Xuan", "Long Bien", "Hoang Mai"]
    )
    
    price_range = st.selectbox(
        "Khoảng giá:",
        ["Tất cả", "Bình dân", "Trung bình", "Cao cấp"]
    )
    
    # Convert to API format
    filters = {}
    if restaurant_type != "Tất cả":
        type_mapping = {
            "Nhà hàng": "restaurant",
            "Bar": "bar",
            "Karaoke": "karaoke",
            "Café": "cafe",
            "Buffet": "buffet"
        }
        if restaurant_type:
            filters['type'] = type_mapping.get(restaurant_type, 'restaurant')
    
    if district and district != "Tất cả":
        filters['district'] = district.replace(" ", "")
    
    if price_range and price_range != "Tất cả":
        price_mapping = {
            "Bình dân": "cheap",
            "Trung bình": "moderate",
            "Cao cấp": "expensive"
        }
        if price_range:
            filters['price'] = price_mapping.get(price_range, 'moderate')
    
    st.markdown("---")
    
    # Settings
    st.markdown("### ⚡ Cài đặt nâng cao")
    
    use_rag = st.checkbox("Sử dụng AI (RAG)", value=True, 
                          help="Bật để nhận câu trả lời từ AI, tắt để chỉ tìm kiếm")
    
    st.markdown("---")
    
    # Clear chat
    if st.button("🗑️ Xóa lịch sử chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.session_state.restaurants = []
        st.rerun()
    
    # About
    with st.expander("ℹ️ Về chatbot"):
        st.markdown("""
        **TopGo AI Chatbot**
        
        Hệ thống gợi ý nhà hàng thông minh sử dụng:
        - 🤖 AI (RAG) với Ollama
        - 🔍 Semantic Search
        - 📊 159 nhà hàng từ TopGo.vn
        
        **Model**: qwen2:7b (Vietnamese-optimized)
        """)


# ========== MAIN CONTENT ==========

# Header
st.markdown("""
<div class="main-header">
    <h1>🍽️ TopGo AI Chatbot</h1>
    <p>Trợ lý AI thông minh giúp bạn tìm nhà hàng hoàn hảo ở Hà Nội</p>
</div>
""", unsafe_allow_html=True)

# ========== CHAT MODE ==========

if mode == "💬 Chat với AI":
    st.markdown("### 💬 Trò chuyện với AI")
    st.caption("Hỏi tôi bất cứ điều gì về nhà hàng, quán bar, karaoke ở Hà Nội!")
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <strong>Bạn:</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="assistant-message">
                <strong>🤖 AI Assistant:</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
    
    # Display restaurants if any
    if st.session_state.restaurants:
        st.markdown("### 📍 Nhà hàng tìm thấy")
        for idx, restaurant in enumerate(st.session_state.restaurants):
            display_restaurant_card(restaurant, idx)
    
    # Chat input
    user_input = st.chat_input("Nhập câu hỏi của bạn...")
    
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.conversation_history.append({"role": "user", "content": user_input})
        
        # Get AI response
        with st.spinner("🤔 AI đang suy nghĩ..."):
            response = chat_with_ai(user_input, filters if filters else None, use_rag)
        
        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": response["answer"]})
        st.session_state.conversation_history.append({"role": "assistant", "content": response["answer"]})
        
        # Store restaurants
        st.session_state.restaurants = response.get("restaurants", [])
        
        # Rerun to display new messages
        st.rerun()
    
    # Sample questions
    if not st.session_state.messages:
        st.markdown("### 💡 Gợi ý câu hỏi:")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🍜 Nhà hàng Việt Nam bình dân", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "Tìm nhà hàng Việt Nam bình dân ở Cầu Giấy"})
                st.rerun()
            
            if st.button("🎤 Karaoke sang trọng", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "Karaoke VIP phù hợp họp lớp 30 người"})
                st.rerun()
        
        with col2:
            if st.button("🍺 Bar view đẹp", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "Quán bar có view đẹp ở Tây Hồ cho hẹn hò"})
                st.rerun()
            
            if st.button("🍱 Buffet cho gia đình", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "Buffet phù hợp gia đình 6 người"})
                st.rerun()


# ========== SEARCH MODE ==========

elif mode == "🔍 Tìm kiếm":
    st.markdown("### 🔍 Tìm kiếm nhà hàng")
    
    search_query = st.text_input(
        "Nhập từ khóa tìm kiếm:",
        placeholder="VD: lẩu Thái, sushi, gà rán..."
    )
    
    if st.button("🔍 Tìm kiếm", type="primary", use_container_width=True):
        if search_query:
            with st.spinner("🔍 Đang tìm kiếm..."):
                results = search_restaurants(search_query, filters)
            
            if results['total_found'] > 0:
                st.success(f"✅ Tìm thấy {results['total_found']} nhà hàng")
                
                for idx, restaurant in enumerate(results['restaurants']):
                    display_restaurant_card(restaurant, idx)
            else:
                st.warning("Không tìm thấy nhà hàng phù hợp. Thử thay đổi từ khóa hoặc bộ lọc!")
        else:
            st.error("Vui lòng nhập từ khóa tìm kiếm!")


# ========== RECOMMENDATION MODE ==========

elif mode == "🎯 Gợi ý":
    st.markdown("### 🎯 Nhận gợi ý cá nhân hóa")
    
    col1, col2 = st.columns(2)
    
    with col1:
        occasion = st.selectbox(
            "Dịp:",
            ["Hẹn hò", "Sinh nhật", "Họp lớp", "Gia đình", "Công ty", "Bạn bè"]
        )
        
        group_size = st.number_input(
            "Số người:",
            min_value=1,
            max_value=100,
            value=2
        )
    
    with col2:
        budget = st.number_input(
            "Ngân sách/người (VNĐ):",
            min_value=0,
            max_value=5000000,
            value=300000,
            step=50000
        )
        
        rec_district = st.selectbox(
            "Khu vực ưu tiên:",
            ["", "Ba Dinh", "Hoan Kiem", "Dong Da", "Hai Ba Trung", 
             "Cau Giay", "Tay Ho", "Thanh Xuan"]
        )
    
    if st.button("🎯 Nhận gợi ý", type="primary", use_container_width=True):
        with st.spinner("🤔 AI đang phân tích..."):
            results = get_recommendations(
                occasion.lower() if occasion else "",
                int(group_size) if group_size else 2,
                int(budget) if budget else 0,
                rec_district.replace(" ", "") if rec_district else ""
            )
        
        if results['total_recommendations'] > 0:
            st.success(f"✨ {results['suggestion_reason']}")
            st.info(f"📊 Tìm thấy {results['total_recommendations']} gợi ý phù hợp")
            
            for idx, restaurant in enumerate(results['recommendations']):
                display_restaurant_card(restaurant, idx)
        else:
            st.warning("Không tìm thấy nhà hàng phù hợp. Thử điều chỉnh các tiêu chí!")


# ========== FOOTER ==========

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🍽️ <strong>TopGo AI Chatbot</strong> - Powered by RAG & Ollama (qwen2:7b)</p>
    <p>📊 159 nhà hàng từ TopGo.vn | 🤖 Vietnamese-optimized AI</p>
</div>
""", unsafe_allow_html=True)

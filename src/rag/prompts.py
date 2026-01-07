"""
Prompt templates for RAG chatbot in Vietnamese
"""
from typing import List, Dict


class PromptTemplates:
    """Vietnamese prompt templates for restaurant recommendation chatbot"""
    
    SYSTEM_PROMPT = """Bạn là trợ lý AI thông minh chuyên tư vấn về nhà hàng, quán bar và karaoke tại Hà Nội.

QUAN TRỌNG: BẠN PHẢI TRẢ LỜI HOÀN TOÀN BẰNG TIẾNG VIỆT!

VAI TRÒ CỦA BẠN:
- Tư vấn và gợi ý địa điểm ăn uống, vui chơi phù hợp với nhu cầu của khách hàng
- Cung cấp thông tin chính xác dựa trên dữ liệu có sẵn
- Trả lời thân thiện, nhiệt tình và hữu ích bằng TIẾNG VIỆT
- Giải thích rõ ràng lý do gợi ý

GIỚI HẠN CHUYÊN MÔN:
- Bạn CHỈ chuyên về tư vấn nhà hàng, quán bar, karaoke tại Hà Nội
- Bạn KHÔNG có khả năng trả lời về: toán học, lịch sử, thời tiết, tin tức, khoa học, hoặc bất kỳ lĩnh vực nào khác
- Nếu người dùng hỏi về lĩnh vực khác, hãy lịch sự từ chối và hướng họ về chức năng tư vấn nhà hàng

QUY TẮC QUAN TRỌNG - NGHIÊM CẤM VI PHẠM:
1. ⛔ TUYỆT ĐỐI CẤM BỊA THÔNG TIN!
   - KHÔNG tự tạo tên nhà hàng, địa chỉ, số điện thoại
   - KHÔNG gợi ý địa điểm nào không có trong DỮ LIỆU được cung cấp
   - CHỈ giới thiệu các địa điểm CÓ TRONG DỮ LIỆU
   
2. PHẢI trả lời HOÀN TOÀN bằng TIẾNG VIỆT - KHÔNG được dùng tiếng Anh

3. CHỈ sử dụng thông tin từ "DỮ LIỆU CÁC ĐỊA ĐIỂM PHÙ HỢP"
   - Copy chính xác: tên, địa chỉ, số điện thoại từ dữ liệu
   - KHÔNG được chỉnh sửa hoặc thay đổi bất kỳ thông tin nào
   
4. Nếu không có dữ liệu → Nói rõ "Không tìm thấy"
   - KHÔNG gợi ý bất kỳ địa điểm cụ thể nào
   - CHỈ đưa ra lời khuyên chung: thử quận khác, điều chỉnh giá, v.v.
   
5. Nếu câu hỏi KHÔNG liên quan đến nhà hàng/ăn uống → Nói rõ bạn chỉ chuyên tư vấn nhà hàng

ĐỊNH DẠNG TRẢ LỜI (Bằng tiếng Việt):
- Mở đầu thân thiện (VD: "Chào bạn!", "Dạ vâng!")
- Giới thiệu ngắn gọn các gợi ý (2-5 địa điểm)
- Chi tiết từng địa điểm với thông tin đầy đủ
- Kết thúc với lời khuyên hoặc gợi ý thêm

VÍ DỤ TRẢ LỜI TỐT:
"Chào bạn! Tôi xin giới thiệu một số nhà hàng phù hợp:

🍽️ Cơm Việt Heritage - nhà hàng bình dân phù hợp gia đình
- Địa chỉ: 17T9 Nguyễn Thị Thập, Cầu Giấy
- Số điện thoại: 0913515351
- Giá cả: Bình dân (dưới 200K/người)
- Đặc điểm: Không gian rộng rãi, thực đơn đa dạng

Bạn nên đặt bàn trước để đảm bảo có chỗ ngồi tốt!"
"""

    QUERY_PROMPT = """Dựa trên thông tin sau đây, hãy tư vấn cho khách hàng BẰNG TIẾNG VIỆT:

CÂU HỎI KHÁCH HÀNG:
{query}

DỮ LIỆU CÁC ĐỊA ĐIỂM PHÙ HỢP:
{context}

⚠️ QUY TẮC BẮT BUỘC:
1. KIỂM TRA dữ liệu trước:
   - NẾU có dữ liệu địa điểm → Giới thiệu các địa điểm đó một cách nhiệt tình
   - NẾU KHÔNG có dữ liệu → Chỉ khi đó mới nói "Rất tiếc, tôi không tìm thấy..."

2. KHI CÓ DỮ LIỆU:
   - CHỈ giới thiệu các địa điểm có trong DỮ LIỆU
   - KHÔNG tự bịa tên, địa chỉ, số điện thoại
   - Phải cung cấp đầy đủ: tên, địa chỉ, số điện thoại
   - ⛔ TUYỆT ĐỐI KHÔNG thay đổi tên quận từ dữ liệu!
     VD: "Hoàn Kiếm" → PHẢI viết "Hoàn Kiếm" (KHÔNG viết "Hoàng Kim")
     VD: "Cầu Giấy" → PHẢI viết "Cầu Giấy" (KHÔNG viết "Cầu Gỗ" hay "Cầu Giầy")
   - Copy CHÍNH XÁC tên quận từ dữ liệu, không sửa đổi!
   - KẾT THÚC bằng lời khuyên hữu ích (đặt bàn trước, thời gian tốt nhất, v.v.)
   - KHÔNG thêm câu "không tìm thấy" khi đã giới thiệu địa điểm

3. CHỈ nói "Rất tiếc, tôi không tìm thấy địa điểm phù hợp" KHI dữ liệu trống hoặc không phù hợp

Hãy trả lời HOÀN TOÀN bằng TIẾNG VIỆT, dựa CHÍNH XÁC vào dữ liệu được cung cấp."""

    @staticmethod
    def format_restaurant_context(restaurants: List[Dict]) -> str:
        """
        Format restaurant data into context string
        
        Args:
            restaurants: List of restaurant dictionaries from search results
            
        Returns:
            Formatted context string
        """
        if not restaurants:
            return "Không tìm thấy địa điểm phù hợp."
        
        context_parts = []
        
        for i, resto in enumerate(restaurants, 1):
            # Extract data
            name = resto.get('name', 'N/A')
            business_type = resto.get('business_type', 'N/A')
            district = resto.get('district', 'N/A')
            price = resto.get('price_range', 'N/A').replace('_', ' ').title()
            phone = resto.get('phone', 'N/A')
            address = resto.get('address', 'N/A')
            
            # Format cuisine types
            cuisine = resto.get('cuisine_type', [])
            if isinstance(cuisine, list):
                cuisine_str = ', '.join([c for c in cuisine if c])
            else:
                cuisine_str = cuisine
            
            # Format features
            features = resto.get('features', [])
            if isinstance(features, list):
                features_str = ', '.join([f for f in features[:5] if f])
            else:
                features_str = features
            
            # Build context for this restaurant
            resto_context = f"""
{i}. {name}
   - Loại hình: {business_type.title()}
   - Quận: {district}
   - Mức giá: {price}
   - Số điện thoại: {phone}
   - Địa chỉ: {address}"""
            
            if cuisine_str:
                resto_context += f"\n   - Ẩm thực: {cuisine_str}"
            
            if features_str:
                resto_context += f"\n   - Đặc điểm: {features_str}"
            
            # Add similarity score if available
            if 'similarity_score' in resto:
                score = resto['similarity_score']
                resto_context += f"\n   - Độ phù hợp: {score:.0%}"
            
            context_parts.append(resto_context)
        
        return "\n".join(context_parts)
    
    @staticmethod
    def build_prompt(query: str, restaurants: List[Dict]) -> str:
        """
        Build complete prompt for LLM
        
        Args:
            query: User query
            restaurants: List of relevant restaurants
            
        Returns:
            Complete prompt string
        """
        context = PromptTemplates.format_restaurant_context(restaurants)
        
        return PromptTemplates.QUERY_PROMPT.format(
            query=query,
            context=context
        )
    
    @staticmethod
    def build_no_results_prompt(query: str) -> str:
        """Build prompt when no results found"""
        return f"""⚠️ CẤM TUYỆT ĐỐI BỊA THÔNG TIN ⚠️

Khách hàng hỏi: "{query}"

CƠ SỞ DỮ LIỆU TRỐNG - KHÔNG CÓ DỮ LIỆU NÀO!

BẠN CHỈ ĐƯỢC PHÉP TRẢ LỜI SAU ĐÂY (KHÔNG THÊM THẮT):

"Rất tiếc, tôi không tìm thấy địa điểm nào phù hợp với yêu cầu của bạn trong cơ sở dữ liệu hiện tại.

Bạn có thể thử:
- Mở rộng khu vực tìm kiếm (thử các quận khác)
- Điều chỉnh mức giá
- Thay đổi loại hình (nhà hàng, bar, karaoke)

Hoặc cho tôi biết thêm chi tiết về nhu cầu của bạn để tôi có thể tư vấn tốt hơn."

⛔ TUYỆT ĐỐI KHÔNG ĐƯỢC:
- Bịa tên nhà hàng
- Bịa địa chỉ
- Bịa số điện thoại
- Gợi ý bất kỳ địa điểm cụ thể nào

CHỈ TRẢ LỜI NỘI DUNG TRÊN - KHÔNG GÌ THÊM!"""

    @staticmethod
    def build_followup_prompt(query: str, context: str, history: List[Dict]) -> str:
        """
        Build prompt for follow-up questions with conversation history
        
        Args:
            query: Current query
            context: Restaurant context
            history: Conversation history
            
        Returns:
            Complete prompt with history
        """
        # Build conversation history
        history_str = "\n\nLỊCH SỬ HỘI THOẠI:\n"
        for msg in history[-3:]:  # Last 3 messages
            role = msg.get('role', '')
            content = msg.get('content', '')
            if role == 'user':
                history_str += f"\nKhách: {content}"
            elif role == 'assistant':
                history_str += f"\nTrợ lý: {content}"
        
        return f"""{history_str}

CÂU HỎI MỚI:
{query}

DỮ LIỆU CÁC ĐỊA ĐIỂM PHÙ HỢP:
{context}

Hãy trả lời câu hỏi mới dựa trên ngữ cảnh cuộc hội thoại và dữ liệu địa điểm."""


# Example usage
if __name__ == "__main__":
    # Example restaurant data
    example_restaurants = [
        {
            'name': 'Cơm Việt Heritage',
            'business_type': 'restaurant',
            'district': 'Cầu Giấy',
            'price_range': 'binh_dan',
            'phone': '0913515351',
            'address': '17T9 Nguyễn Thị Thập, Trung Hoà, Cầu Giấy',
            'cuisine_type': ['Việt', 'Âu'],
            'features': ['Gia Đình', 'Sang Trọng'],
            'similarity_score': 0.85
        },
        {
            'name': 'Le Cabaret Restaurant',
            'business_type': 'bar',
            'district': 'Hoàn Kiếm',
            'price_range': 'cao_cap',
            'phone': '0913515351',
            'address': 'Hoàn Kiếm, Hà Nội',
            'cuisine_type': ['Âu'],
            'features': ['Hẹn Hò', 'View Đẹp'],
            'similarity_score': 0.78
        }
    ]
    
    # Test formatting
    print("=" * 80)
    print("SYSTEM PROMPT:")
    print("=" * 80)
    print(PromptTemplates.SYSTEM_PROMPT)
    
    print("\n" + "=" * 80)
    print("CONTEXT FORMATTING:")
    print("=" * 80)
    context = PromptTemplates.format_restaurant_context(example_restaurants)
    print(context)
    
    print("\n" + "=" * 80)
    print("COMPLETE PROMPT:")
    print("=" * 80)
    prompt = PromptTemplates.build_prompt(
        query="Tìm nhà hàng Việt Nam bình dân cho gia đình",
        restaurants=example_restaurants
    )
    print(prompt)

"""
RAG Pipeline: Retrieval-Augmented Generation for restaurant recommendations
"""
from typing import Dict, List, Optional
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.embeddings.search_engine import RestaurantSearchEngine
from src.llm.ollama_client import OllamaClient
from src.rag.prompts import PromptTemplates


class RAGPipeline:
    """
    RAG Pipeline combining semantic search with LLM generation
    """
    
    def __init__(
        self,
        model: str = "qwen2:1.5b",
        ollama_url: str = "http://localhost:11434",
        search_top_k: int = 5
    ):
        """
        Initialize RAG pipeline with Ollama (Local LLM)
        
        Args:
            model: Ollama model name (qwen2:1.5b, llama2, mistral, etc.)
            ollama_url: Ollama API URL (default: http://localhost:11434)
            search_top_k: Number of restaurants to retrieve
        """
        print("🔄 Initializing RAG Pipeline (Ollama Local LLM)...")
        
        # Initialize components
        self.search_engine = RestaurantSearchEngine()
        self.prompt_templates = PromptTemplates()
        self.search_top_k = search_top_k
        self.model = model
        
        # Initialize Ollama
        self.llm = OllamaClient(base_url=ollama_url, model=model)
        
        # Check Ollama connection
        if not self.llm.check_connection():
            print("⚠️  Warning: Ollama is not running!")
            print("   Start Ollama with: ollama serve")
            print("   Pipeline will work in search-only mode")
            self.ollama_available = False
        else:
            print(f"✅ Ollama connected! Model: {model}")
            self.ollama_available = True
        
        print("✅ RAG Pipeline ready!\n")
    
    @property
    def llm_available(self) -> bool:
        """Check if Ollama LLM is available"""
        return self.ollama_available
    
    def _llm_generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.7, max_tokens: int = 800) -> str:
        """
        Generate text using Ollama
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            temperature: Temperature
            max_tokens: Max tokens
            
        Returns:
            Generated text
        """
        return self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def retrieve(
        self,
        query: str,
        filters: Optional[Dict] = None,
        top_k: Optional[int] = None
    ) -> List[Dict]:
        """
        Retrieve relevant restaurants using semantic search
        
        Args:
            query: User query
            filters: Optional filters (business_type, district, price_range)
            top_k: Number of results (defaults to search_top_k)
            
        Returns:
            List of relevant restaurants
        """
        k = top_k or self.search_top_k
        
        # Use search with filters - ChromaDB will handle multiple filters
        return self.search_engine.search(query, n_results=k, filters=filters)
    
    def generate(
        self,
        query: str,
        context_restaurants: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 800
    ) -> str:
        """
        Generate answer using LLM with retrieved context
        
        Args:
            query: User query
            context_restaurants: Retrieved restaurants
            temperature: LLM temperature
            max_tokens: Max tokens to generate
            
        Returns:
            Generated answer
        """
        
        if not self.llm_available:
            # Return search results without LLM
            return self._format_search_only_response(context_restaurants)
        
        # IMPORTANT: If no results, return directly without calling LLM to avoid hallucination
        if not context_restaurants:
            return """Rất tiếc, tôi không tìm thấy địa điểm nào phù hợp với yêu cầu của bạn trong cơ sở dữ liệu hiện tại.

Bạn có thể thử:
- Mở rộng khu vực tìm kiếm (thử các quận khác)
- Điều chỉnh mức giá  
- Thay đổi loại hình (nhà hàng, bar, karaoke)

Hoặc cho tôi biết thêm chi tiết về nhu cầu của bạn để tôi có thể tư vấn tốt hơn."""
        
        # Build prompt with restaurant data
        prompt = PromptTemplates.build_prompt(query, context_restaurants)
        
        # Generate with LLM
        response = self._llm_generate(
            prompt=prompt,
            system_prompt=PromptTemplates.SYSTEM_PROMPT,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Post-process: Validate that LLM didn't change district names
        if context_restaurants:
            # Get actual districts from data
            actual_districts = set(r.get('district', '') for r in context_restaurants)
            
            # Common LLM mistakes mapping
            district_corrections = {
                'hoàng kim': 'Hoàn Kiếm',
                'hoang kim': 'Hoàn Kiếm', 
                'cầu gỗ': 'Cầu Giấy',
                'cau go': 'Cầu Giấy',
                'cầu giầy': 'Cầu Giấy',
                'tây hô': 'Tây Hồ',
                'tay ho': 'Tây Hồ',
                'đồng đa': 'Đống Đa',
                'dong da': 'Đống Đa'
            }
            
            # Check and fix common mistakes in response
            response_lower = response.lower()
            for wrong, correct in district_corrections.items():
                if wrong in response_lower and correct in actual_districts:
                    # Case-insensitive replacement
                    import re
                    pattern = re.compile(re.escape(wrong), re.IGNORECASE)
                    response = pattern.sub(correct, response)
                    print(f"⚠️  Fixed LLM mistake: '{wrong}' → '{correct}'")
        
        # Post-process: Remove "không tìm thấy" if restaurants were introduced
        if context_restaurants and len(response) > 100:
            # If response is long and has restaurant info, remove any "not found" messages
            negative_phrases = [
                "Rất tiếc, tôi không tìm thấy",
                "Xin lỗi, không tìm thấy",
                "Không tìm thấy địa điểm phù hợp"
            ]
            for phrase in negative_phrases:
                if phrase in response:
                    # Split by the negative phrase and keep only the part before it
                    response = response.split(phrase)[0].strip()
        
        return response
    
    def _classify_query_with_llm(self, query: str) -> Dict:
        """
        Use LLM to classify user query and determine if restaurant search is needed
        
        Args:
            query: User query
            
        Returns:
            Dict with 'needs_search' (bool) and 'response_type' (str)
        """
        if not self.llm_available:
            # Fallback: assume all queries need search
            return {'needs_search': True, 'response_type': 'restaurant_query'}
        
        # Pre-classification using keywords (faster and more reliable)
        query_lower = query.lower()
        
        # Strong restaurant/bar/karaoke indicators
        restaurant_keywords = [
            'nhà hàng', 'quán ăn', 'quán', 'bar', 'pub', 'karaoke',
            'buffet', 'restaurant', 'cafe', 'quán cafe',
            'ăn', 'món', 'đồ ăn', 'thức ăn', 'bữa', 'cơm', 'phở',
            'bún', 'mì', 'lẩu', 'nướng', 'dimsum',
            'quận', 'ở đâu', 'gần', 'phù hợp', 'tốt', 'ngon',
            'giá rẻ', 'bình dân', 'sang trọng', 'cao cấp',
            'trung bình', 'gợi ý', 'giới thiệu', 'tìm', 'cho tôi',
            'tây', 'ý', 'nhật', 'hàn', 'trung', 'việt', 'âu', 'á',
            'cầu giấy', 'tây hồ', 'hoàn kiếm', 'ba đình', 'đống đa',
            'hai bà trưng', 'thanh xuân', 'long biên', 'hoàng mai'
        ]
        
        # Check if query contains restaurant-related keywords
        has_restaurant_keyword = any(keyword in query_lower for keyword in restaurant_keywords)
        
        # Strong greeting indicators (only if NO restaurant keywords)
        greeting_keywords = ['xin chào', 'chào', 'hello', 'hi', 'hey']
        is_pure_greeting = any(query_lower.strip() == greeting for greeting in greeting_keywords)
        
        # If has restaurant keywords, classify as restaurant_query immediately
        if has_restaurant_keyword:
            return {'needs_search': True, 'response_type': 'restaurant_query'}
        
        # If pure greeting only
        if is_pure_greeting:
            return {'needs_search': False, 'response_type': 'greeting'}
        
        # Otherwise, use LLM for ambiguous cases
        classification_prompt = f"""Phân tích câu hỏi của người dùng và trả lời theo format JSON:

Câu hỏi: "{query}"

Hãy xác định:
1. Người dùng có đang TÌM KIẾM nhà hàng/quán bar/karaoke cụ thể không?
2. Hay chỉ đang chào hỏi/hỏi thông tin chung về chatbot?

Trả lời CHÍNH XÁC theo format JSON này (không giải thích thêm):
{{
    "needs_search": true/false,
    "response_type": "greeting" hoặc "general_question" hoặc "restaurant_query",
    "reasoning": "lý do ngắn gọn"
}}

VÍ DỤ:
- "hello" → {{"needs_search": false, "response_type": "greeting", "reasoning": "Chỉ chào hỏi"}}
- "bạn là ai" → {{"needs_search": false, "response_type": "general_question", "reasoning": "Hỏi về chatbot"}}
- "tìm nhà hàng bình dân" → {{"needs_search": true, "response_type": "restaurant_query", "reasoning": "Tìm nhà hàng cụ thể"}}
- "quán nào ngon ở cầu giấy" → {{"needs_search": true, "response_type": "restaurant_query", "reasoning": "Hỏi về địa điểm"}}

Chỉ trả về JSON, không có text khác."""

        try:
            response = self._llm_generate(
                prompt=classification_prompt,
                system_prompt="Bạn là AI phân loại câu hỏi. Chỉ trả về JSON, không giải thích thêm.",
                temperature=0.1,
                max_tokens=150
            )
            
            # Parse JSON response
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                # Fallback if can't parse
                return {'needs_search': True, 'response_type': 'restaurant_query'}
                
        except Exception as e:
            print(f"⚠️  Classification error: {e}")
            # Fallback: assume restaurant query
            return {'needs_search': True, 'response_type': 'restaurant_query'}
    
    def _generate_conversational_response(self, query: str, response_type: str) -> str:
        """
        Generate natural conversational response using LLM (no restaurant search)
        
        Args:
            query: User query
            response_type: Type of response (greeting, general_question)
            
        Returns:
            Natural response from LLM
        """
        if not self.llm_available:
            return "Xin chào! Tôi là trợ lý tư vấn nhà hàng tại Hà Nội. Bạn cần tìm loại địa điểm nào?"
        
        # Check if query is about non-restaurant topics
        non_restaurant_keywords = [
            'toán', 'tính', '+', '-', '*', '/', 'bằng mấy', 'kết quả',
            'thời tiết', 'trời', 'nắng', 'mưa', 'nhiệt độ',
            'tin tức', 'bóng đá', 'chính trị', 'kinh tế',
            'lịch sử', 'địa lý', 'khoa học', 'vật lý', 'hóa học',
            'code', 'lập trình', 'python', 'javascript'
        ]
        
        query_lower = query.lower()
        is_non_restaurant = any(keyword in query_lower for keyword in non_restaurant_keywords)
        
        if is_non_restaurant:
            return """Xin lỗi bạn, tôi là chuyên viên tư vấn về nhà hàng, quán bar và karaoke tại Hà Nội. Tôi không có khả năng trả lời về các vấn đề khác.

Tôi chỉ có thể giúp bạn:
- Tìm nhà hàng phù hợp
- Gợi ý quán bar, karaoke
- Tư vấn địa điểm ăn uống theo nhu cầu

Bạn cần tìm loại địa điểm nào?"""
        
        # For greetings and general questions about the bot
        if response_type == 'greeting':
            return """Xin chào! Tôi là trợ lý AI chuyên tư vấn về nhà hàng, quán bar và karaoke tại Hà Nội.

Tôi có thể giúp bạn:
- Tìm nhà hàng theo loại hình, quận, mức giá
- Gợi ý địa điểm phù hợp cho các dịp đặc biệt
- Tư vấn quán bar, karaoke

Bạn đang tìm loại địa điểm nào?"""
        
        conversation_prompt = f"""Người dùng hỏi: {query}

Trả lời NGẮN GỌN (2-3 câu) bằng TIẾNG VIỆT:

Nếu hỏi về BẠN:
- Giới thiệu: "Tôi là trợ lý AI chuyên tư vấn nhà hàng, quán bar và karaoke tại Hà Nội."
- Chức năng: "Tôi có thể giúp bạn tìm địa điểm ăn uống phù hợp với nhu cầu."
- Hỏi ngược: "Bạn cần tìm loại địa điểm nào?"

KHÔNG liệt kê nhà hàng cụ thể."""

        response = self._llm_generate(
            prompt=conversation_prompt,
            system_prompt="Bạn là trợ lý AI chuyên tư vấn nhà hàng tại Hà Nội. Trả lời ngắn gọn, thân thiện.",
            temperature=0.5,
            max_tokens=150
        )
        
        return response
    
    def _validate_district_in_query(self, query: str) -> tuple:
        """
        Check if query mentions a valid Hanoi district
        Returns (is_valid, invalid_district_name)
        """
        VALID_DISTRICTS = {
            'ba đình', 'ba dinh', 'hoàn kiếm', 'hoan kiem', 'tây hồ', 'tay ho',
            'long biên', 'long bien', 'cầu giấy', 'cau giay', 'đống đa', 'dong da',
            'hai bà trưng', 'hai ba trung', 'hoàng mai', 'hoang mai', 'thanh xuân', 'thanh xuan',
            'từ liêm', 'tu liem', 'nam từ liêm', 'nam tu liem', 'bắc từ liêm', 'bac tu liem',
            'sóc sơn', 'soc son', 'đông anh', 'dong anh', 'gia lâm', 'gia lam',
            'thanh trì', 'thanh tri', 'hà đông', 'ha dong', 'sơn tây', 'son tay',
            'ba vì', 'ba vi', 'phúc thọ', 'phuc tho', 'đan phượng', 'dan phuong',
            'hoài đức', 'hoai duc', 'quốc oai', 'quoc oai', 'thạch thất', 'thach that',
            'chương mỹ', 'chuong my', 'thanh oai', 'mỹ đức', 'my duc',
            'ứng hòa', 'ung hoa', 'thường tín', 'thuong tin', 'phú xuyên', 'phu xuyen',
            'mê linh', 'me linh'
        }
        
        query_lower = query.lower()
        
        # Check if query mentions district/quận
        if 'quận' in query_lower or 'district' in query_lower:
            # Extract potential district name after these keywords
            import re
            # Match "quận X" or "district X" - capture everything after quận/district until space or punctuation
            # This will catch numbers, special chars, and text
            pattern = r'(?:quận|district)\s+([^,\.\?!\n]+?)(?:\s+(?:nhà|quán|bar|restaurant|karaoke|giá|rẻ|sang|$)|$)'
            
            match = re.search(pattern, query_lower)
            if match:
                mentioned_district = match.group(1).strip()
                
                # Additional cleanup: remove trailing words that might be captured
                # Split and take only first 3 words max for district name
                district_words = mentioned_district.split()
                if len(district_words) > 3:
                    mentioned_district = ' '.join(district_words[:3])
                
                mentioned_district = mentioned_district.strip()
                
                # Check if it's a valid district
                if mentioned_district and mentioned_district not in VALID_DISTRICTS:
                    print(f"⚠️  Invalid district in query: '{mentioned_district}'")
                    return False, mentioned_district
        
        return True, ""
    
    def _extract_filters_from_query(self, query: str) -> Dict:
        """
        Use LLM to extract filters from user query
        
        Args:
            query: User query
            
        Returns:
            Dict with extracted filters (district, business_type, price_range)
        """
        if not self.llm_available:
            return {}
        
        # Pre-validate district in query
        is_valid, invalid_district = self._validate_district_in_query(query)
        if not is_valid:
            print(f"   ⛔ Query contains invalid district '{invalid_district}' - returning special marker")
            return {'_invalid_district': invalid_district}
        
        extraction_prompt = f"""Phân tích câu hỏi và trích xuất thông tin:

Câu hỏi: "{query}"

Tìm các thông tin sau (NẾU CÓ trong câu hỏi):
1. Quận (CHỈ các quận HỢP LỆ ở Hà Nội): Tây Hồ, Hoàn Kiếm, Cầu Giấy, Ba Đình, Đống Đa, Hai Bà Trưng, Thanh Xuân, Long Biên, Hoàng Mai
2. Loại: restaurant (nhà hàng), bar (quán bar), karaoke  
3. Giá: binh_dan (bình dân/rẻ), trung_binh (trung bình), cao_cap (sang/cao cấp)

QUAN TRỌNG:
- CHỈ trích xuất quận NẾU nó là quận THẬT của Hà Nội
- NẾU quận KHÔNG HỢP LỆ (ví dụ: "sao Hỏa", "sao Mars", v.v.) → KHÔNG trả về district
- KHÔNG tự sửa hoặc đoán tên quận
- price_range: "binh_dan" hoặc "trung_binh" hoặc "cao_cap" (chữ thường, gạch dưới)
- business_type: "restaurant" hoặc "bar" hoặc "karaoke"
- Nếu KHÔNG chắc chắn → bỏ qua key đó

Trả lời CHÍNH XÁC theo format JSON (KHÔNG thêm text):
{{
    "district": "Tây Hồ",
    "business_type": "restaurant",
    "price_range": "binh_dan"
}}

Bây giờ trích xuất (chỉ JSON):"""

        try:
            response = self._llm_generate(
                prompt=extraction_prompt,
                system_prompt="Trả về JSON. KHÔNG giải thích.",
                temperature=0.1,
                max_tokens=100
            )
            
            # Parse JSON
            import json
            import re
            
            json_match = re.search(r'\{[^}]*\}', response, re.DOTALL)
            if json_match:
                filters = json.loads(json_match.group())
                
                # Valid Hanoi districts (normalized)
                VALID_DISTRICTS = {
                    'ba đình', 'ba dinh', 'hoàn kiếm', 'hoan kiem', 'tây hồ', 'tay ho',
                    'long biên', 'long bien', 'cầu giấy', 'cau giay', 'đống đa', 'dong da',
                    'hai bà trưng', 'hai ba trung', 'hoàng mai', 'hoang mai', 'thanh xuân', 'thanh xuan',
                    'từ liêm', 'tu liem', 'nam từ liêm', 'nam tu liem', 'bắc từ liêm', 'bac tu liem',
                    'sóc sơn', 'soc son', 'đông anh', 'dong anh', 'gia lâm', 'gia lam',
                    'thanh trì', 'thanh tri', 'hà đông', 'ha dong', 'sơn tây', 'son tay',
                    'ba vì', 'ba vi', 'phúc thọ', 'phuc tho', 'đan phượng', 'dan phuong',
                    'hoài đức', 'hoai duc', 'quốc oai', 'quoc oai', 'thạch thất', 'thach that',
                    'chương mỹ', 'chuong my', 'thanh oai', 'mỹ đức', 'my duc',
                    'ứng hòa', 'ung hoa', 'thường tín', 'thuong tin', 'phú xuyên', 'phu xuyen',
                    'mê linh', 'me linh', 'thường tín', 'thuong tin'
                }
                
                # Validate and clean filters
                valid_filters = {}
                
                # Check district - MUST be valid Hanoi district
                if 'district' in filters and filters['district']:
                    dist = filters['district'].strip()
                    dist_normalized = dist.lower()
                    
                    # Only accept if it's a real Hanoi district
                    if dist_normalized in VALID_DISTRICTS:
                        valid_filters['district'] = dist
                    else:
                        print(f"⚠️  Invalid district from LLM: '{dist}' - not in Hanoi district list")
                
                # Check business_type
                if 'business_type' in filters and filters['business_type']:
                    btype = filters['business_type'].strip().lower()
                    if btype in ['restaurant', 'bar', 'karaoke']:
                        valid_filters['business_type'] = btype
                
                # Check price_range
                if 'price_range' in filters and filters['price_range']:
                    price = filters['price_range'].strip()
                    # Map to database format (lowercase with underscore)
                    price_map = {
                        'binh dan': 'binh_dan',
                        'binh_dan': 'binh_dan',
                        'trung binh': 'trung_binh',
                        'trung_binh': 'trung_binh',
                        'cao cap': 'cao_cap',
                        'cao_cap': 'cao_cap'
                    }
                    normalized = price_map.get(price.lower(), None)
                    if normalized:
                        valid_filters['price_range'] = normalized
                
                return valid_filters
            else:
                return {}
                
        except Exception as e:
            print(f"⚠️  Filter extraction error: {e}")
            return {}
    
    def answer(
        self,
        query: str,
        filters: Optional[Dict] = None,
        top_k: Optional[int] = None,
        temperature: float = 0.7,
        max_tokens: int = 800,
        return_sources: bool = True
    ) -> Dict:
        """
        Complete RAG pipeline: retrieve + generate
        
        Args:
            query: User query
            filters: Optional filters (if None, will auto-extract from query)
            top_k: Number of restaurants to retrieve
            temperature: LLM temperature
            max_tokens: Max tokens
            return_sources: Whether to return source restaurants
            
        Returns:
            Dictionary with answer and optionally sources
        """
        # Step 1: Classify query using LLM
        print(f"🤔 Analyzing query: '{query}'")
        classification = self._classify_query_with_llm(query)
        print(f"   Classification: {classification.get('response_type')} (needs_search: {classification.get('needs_search')})")
        
        # Step 2: Handle based on classification
        if not classification.get('needs_search', True):
            # No search needed - generate conversational response
            print(f"💬 Generating conversational response...")
            response_type = classification.get('response_type', 'greeting')
            answer = self._generate_conversational_response(query, response_type)
            return {
                'query': query,
                'answer': answer,
                'num_sources': 0,
                'sources': [] if return_sources else None
            }
        
        # Step 3: Auto-extract filters from query if not provided
        if not filters:
            print(f"🔍 Extracting filters from query...")
            filters = self._extract_filters_from_query(query)
            
            # Check if invalid district was detected
            if filters and '_invalid_district' in filters:
                invalid_district = filters['_invalid_district']
                print(f"   ❌ Invalid district detected: '{invalid_district}'")
                answer = f"Xin lỗi, quận '{invalid_district}' không tồn tại tại Hà Nội. Hà Nội có các quận sau: Hoàn Kiếm, Ba Đình, Tây Hồ, Cầu Giấy, Đống Đa, Hai Bà Trưng, Thanh Xuân, Long Biên, Hoàng Mai, Hà Đông và các huyện ngoại thành. Bạn có thể chọn một quận khác."
                return {
                    'query': query,
                    'answer': answer,
                    'num_sources': 0,
                    'sources': [] if return_sources else None
                }
            
            if filters:
                print(f"   Extracted filters: {filters}")
        
        # Do search + generation
        print(f"🔍 Searching for: '{query}'")
        restaurants = self.retrieve(query, filters, top_k)
        print(f"   Found {len(restaurants)} relevant restaurants")
        
        # Generate response with error handling
        if self.llm_available:
            try:
                print(f"🤖 Generating response with LLM...")
                answer = self.generate(query, restaurants, temperature, max_tokens)
            except Exception as e:
                print(f"⚠️  LLM error (quota exceeded or other): {str(e)[:100]}")
                print(f"📋 Fallback: Returning search results without LLM...")
                answer = self._format_search_only_response(restaurants)
        else:
            print(f"📋 No LLM available - Returning search results...")
            answer = self._format_search_only_response(restaurants)
        
        # Build result
        result = {
            'query': query,
            'answer': answer,
            'num_sources': len(restaurants)
        }
        
        if return_sources:
            result['sources'] = restaurants
        
        return result
    
    def _format_search_only_response(self, restaurants: List[Dict]) -> str:
        """Format response when Ollama is not available"""
        if not restaurants:
            return "Không tìm thấy địa điểm phù hợp với yêu cầu của bạn."
        
        response = f"Tìm thấy {len(restaurants)} địa điểm phù hợp:\n\n"
        
        for i, resto in enumerate(restaurants, 1):
            response += f"{i}. {resto['name']}\n"
            response += f"   - Loại: {resto['business_type'].title()}\n"
            response += f"   - Quận: {resto['district']}\n"
            response += f"   - Giá: {resto['price_range'].replace('_', ' ').title()}\n"
            response += f"   - SĐT: {resto['phone']}\n"
            response += f"   - Địa chỉ: {resto['address']}\n"
            
            if resto.get('cuisine_type'):
                cuisines = ', '.join([c for c in resto['cuisine_type'] if c])
                if cuisines:
                    response += f"   - Ẩm thực: {cuisines}\n"
            
            response += "\n"
        
        return response
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        filters: Optional[Dict] = None,
        top_k: Optional[int] = None
    ) -> Dict:
        """
        Chat with conversation history
        
        Args:
            messages: Conversation history [{'role': 'user', 'content': '...'}]
            filters: Optional filters
            top_k: Number of results
            
        Returns:
            Response dict
        """
        # Get last user message
        user_messages = [m for m in messages if m.get('role') == 'user']
        if not user_messages:
            return {'error': 'No user message found'}
        
        query = user_messages[-1].get('content', '')
        
        # Use regular answer method
        return self.answer(query, filters, top_k)


def main():
    """Test RAG pipeline"""
    print("=" * 80)
    print("🤖 RAG PIPELINE TEST")
    print("=" * 80)
    
    # Initialize pipeline
    pipeline = RAGPipeline(model="llama2", search_top_k=5)
    
    # Test queries
    test_queries = [
        {
            'query': 'Tìm nhà hàng Việt Nam bình dân cho gia đình ở Cầu Giấy',
            'filters': None
        },
        {
            'query': 'Quán karaoke sang trọng có phòng VIP',
            'filters': {'business_type': 'karaoke'}
        },
        {
            'query': 'Bar có view đẹp phù hợp hẹn hò ở Hoàn Kiếm',
            'filters': {'district': 'Hoàn Kiếm'}
        },
        {
            'query': 'Nơi tổ chức tiệc công ty giá bình dân',
            'filters': {'price_range': 'Binh Dan'}
        }
    ]
    
    for i, test in enumerate(test_queries, 1):
        print("\n" + "=" * 80)
        print(f"TEST {i}")
        print("=" * 80)
        print(f"Query: {test['query']}")
        if test.get('filters'):
            print(f"Filters: {test['filters']}")
        print("-" * 80)
        
        # Get answer
        result = pipeline.answer(
            query=test['query'],
            filters=test.get('filters'),
            temperature=0.7,
            return_sources=True
        )
        
        # Display answer
        print("\n📝 ANSWER:")
        print(result['answer'])
        
        # Display sources
        print(f"\n📚 SOURCES ({result['num_sources']} restaurants):")
        for j, source in enumerate(result.get('sources', [])[:3], 1):
            print(f"\n{j}. {source['name']}")
            print(f"   {source['business_type'].title()} | {source['district']} | {source['price_range'].replace('_', ' ').title()}")
            print(f"   📞 {source['phone']}")
            print(f"   🎯 Similarity: {source['similarity_score']:.2%}")
        
        print("\n" + "=" * 80)
        
        # Pause between tests
        if i < len(test_queries):
            input("\n⏎ Press Enter for next test...")
    
    print("\n✅ All tests complete!")


if __name__ == "__main__":
    main()

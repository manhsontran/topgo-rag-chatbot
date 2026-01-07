"""
Semantic search engine for restaurant recommendations
"""
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from sentence_transformers import SentenceTransformer


class RestaurantSearchEngine:
    """Search engine for finding restaurants using semantic search"""
    
    # Valid districts in Hanoi
    VALID_DISTRICTS = {
        'ba đình', 'ba dinh',
        'hoàn kiếm', 'hoan kiem',
        'tây hồ', 'tay ho',
        'long biên', 'long bien',
        'cầu giấy', 'cau giay',
        'đống đa', 'dong da',
        'hai bà trưng', 'hai ba trung',
        'hoàng mai', 'hoang mai',
        'thanh xuân', 'thanh xuan',
        'sóc sơn', 'soc son',
        'đông anh', 'dong anh',
        'gia lâm', 'gia lam',
        'nam từ liêm', 'nam tu liem',
        'thanh trì', 'thanh tri',
        'bắc từ liêm', 'bac tu liem',
        'mê linh', 'me linh',
        'hà đông', 'ha dong',
        'sơn tây', 'son tay',
        'ba vì', 'ba vi',
        'phúc thọ', 'phuc tho',
        'đan phượng', 'dan phuong',
        'hoài đức', 'hoai duc',
        'quốc oai', 'quoc oai',
        'thạch thất', 'thach that',
        'chương mỹ', 'chuong my',
        'thanh oai', 'thanh oai',
        'thường tín', 'thuong tin',
        'phú xuyên', 'phu xuyen',
        'ứng hòa', 'ung hoa',
        'mỹ đức', 'my duc'
    }
    
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialize search engine
        
        Args:
            model_name: HuggingFace model for embeddings
        """
        # Load embedding model
        self.model = SentenceTransformer(model_name)
        
        # Connect to ChromaDB
        db_path = Path(__file__).parent.parent.parent / "data" / "vector_db"
        self.client = chromadb.PersistentClient(path=str(db_path))
        
        # Get collection
        try:
            self.collection = self.client.get_collection(name="restaurants")
        except Exception as e:
            raise RuntimeError(
                f"Could not find 'restaurants' collection. "
                f"Please run create_embeddings.py first. Error: {e}"
            )
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for restaurants using semantic search
        
        Args:
            query: Search query in Vietnamese
            n_results: Number of results to return
            filters: Optional filters like {'business_type': 'restaurant', 'district': 'Tây Hồ'}
        
        Returns:
            List of restaurant dictionaries with metadata
        """
        # Validate district filter
        if filters and 'district' in filters:
            district_input = filters['district'].lower().strip()
            
            # Check if district is valid
            if district_input not in self.VALID_DISTRICTS:
                # Invalid district - return empty results
                print(f"⚠️  Invalid district: '{filters['district']}' - Not a valid Hanoi district")
                return []
        
        # Create query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        # Build where clause for ChromaDB
        where = None
        if filters:
            # If single filter, use directly
            if len(filters) == 1:
                where = filters  # type: ignore
            # If multiple filters, use $and operator
            elif len(filters) > 1:
                where = {
                    "$and": [
                        {key: value} for key, value in filters.items()
                    ]
                }  # type: ignore
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results,
            where=where  # type: ignore
        )
        
        # Format results
        formatted_results = []
        
        # Check if results are valid
        if not results or not results.get('ids') or not results['ids']:
            return formatted_results
        
        # Safely get result arrays with proper type checking
        ids_list = results.get('ids')
        metadatas_list = results.get('metadatas')
        distances_list = results.get('distances')
        
        if not ids_list or not metadatas_list or not distances_list:
            return formatted_results
        
        ids = ids_list[0] if ids_list else []
        metadatas = metadatas_list[0] if metadatas_list else []
        distances = distances_list[0] if distances_list else []
        
        if not ids:
            return formatted_results
        
        for i, (doc_id, metadata, distance) in enumerate(zip(ids, metadatas, distances)):
            # ChromaDB returns squared euclidean distance
            # Convert to similarity score (0-1 range, higher is better)
            # For squared euclidean: similarity = 1 / (1 + distance)
            # This ensures: distance=0 → similarity=1, distance→∞ → similarity→0
            similarity = 1 / (1 + distance)
            
            # Safely extract metadata with type checking
            cuisine_type_raw = metadata.get('cuisine_type', '')
            features_raw = metadata.get('features', '')
            
            # Handle cuisine_type - could be string or other types
            cuisine_type = []
            if isinstance(cuisine_type_raw, str) and cuisine_type_raw:
                cuisine_type = [c.strip() for c in cuisine_type_raw.split(',') if c.strip()]
            
            # Handle features - could be string or other types
            features = []
            if isinstance(features_raw, str) and features_raw:
                features = [f.strip() for f in features_raw.split(',') if f.strip()]
            
            result = {
                'id': doc_id,
                'name': metadata.get('name', ''),
                'business_type': metadata.get('business_type', ''),
                'district': metadata.get('district', ''),
                'price_range': metadata.get('price_range', ''),
                'phone': metadata.get('phone', ''),
                'address': metadata.get('address', ''),
                'url': metadata.get('url', ''),
                'cuisine_type': cuisine_type,
                'features': features,
                'similarity_score': similarity,
                'rank': i + 1
            }
            formatted_results.append(result)
        
        return formatted_results
    
    def search_by_type(
        self,
        query: str,
        business_type: str,
        n_results: int = 5
    ) -> List[Dict]:
        """
        Search with business type filter
        
        Args:
            query: Search query
            business_type: 'restaurant', 'karaoke', or 'bar'
            n_results: Number of results
        """
        return self.search(
            query=query,
            n_results=n_results,
            filters={'business_type': business_type}
        )
    
    def search_by_district(
        self,
        query: str,
        district: str,
        n_results: int = 5
    ) -> List[Dict]:
        """
        Search with district filter
        
        Args:
            query: Search query
            district: District name (e.g., 'Cầu Giấy')
            n_results: Number of results
        """
        return self.search(
            query=query,
            n_results=n_results,
            filters={'district': district}
        )
    
    def search_by_price(
        self,
        query: str,
        price_range: str,
        n_results: int = 5
    ) -> List[Dict]:
        """
        Search with price range filter
        
        Args:
            query: Search query
            price_range: 'Binh Dan', 'Trung Binh', or 'Cao Cap'
            n_results: Number of results
        """
        return self.search(
            query=query,
            n_results=n_results,
            filters={'price_range': price_range}
        )


def main():
    """Test the search engine"""
    print("🔍 Initializing Restaurant Search Engine...\n")
    
    # Create search engine
    engine = RestaurantSearchEngine()
    
    # Test queries
    test_cases = [
        {
            'query': 'Nhà hàng Việt Nam phù hợp gia đình',
            'description': 'General search for Vietnamese family restaurant'
        },
        {
            'query': 'Karaoke sang trọng',
            'description': 'Luxury karaoke',
            'type': 'karaoke'
        },
        {
            'query': 'Quán bar view đẹp',
            'description': 'Bar with nice view',
            'type': 'bar'
        },
        {
            'query': 'Nhà hàng lãng mạn cho hẹn hò',
            'description': 'Romantic restaurant for dating',
            'district': 'Hoàn Kiếm'
        },
        {
            'query': 'Quán ăn bình dân',
            'description': 'Budget-friendly restaurant',
            'price': 'Binh Dan'
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print("=" * 80)
        print(f"TEST {i}: {test['description']}")
        print(f"Query: '{test['query']}'")
        
        if 'type' in test:
            print(f"Filter: business_type = {test['type']}")
            results = engine.search_by_type(test['query'], test['type'], n_results=3)
        elif 'district' in test:
            print(f"Filter: district = {test['district']}")
            results = engine.search_by_district(test['query'], test['district'], n_results=3)
        elif 'price' in test:
            print(f"Filter: price_range = {test['price']}")
            results = engine.search_by_price(test['query'], test['price'], n_results=3)
        else:
            results = engine.search(test['query'], n_results=3)
        
        print("=" * 80)
        print("\n🎯 Results:\n")
        
        for result in results:
            print(f"{result['rank']}. {result['name']}")
            print(f"   Type: {result['business_type']} | District: {result['district']} | Price: {result['price_range']}")
            print(f"   Phone: {result['phone']}")
            print(f"   Similarity: {result['similarity_score']:.4f}")
            print(f"   URL: {result['url']}\n")
        
        print()


if __name__ == "__main__":
    main()

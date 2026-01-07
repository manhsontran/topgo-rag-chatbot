"""
Create embeddings for restaurant data using sentence-transformers
and store in ChromaDB for semantic search
"""
import json
import os
from pathlib import Path
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


class EmbeddingCreator:
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialize embedding creator
        
        Args:
            model_name: HuggingFace model for embeddings (supports Vietnamese)
        """
        print(f"🔄 Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("✅ Model loaded successfully!")
        
        # Setup ChromaDB
        self.db_path = Path(__file__).parent.parent.parent / "data" / "vector_db"
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 ChromaDB path: {self.db_path}")
        self.client = chromadb.PersistentClient(path=str(self.db_path))
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="restaurants",
            metadata={"description": "TopGo restaurant embeddings"}
        )
        
    def load_data(self, filepath: str) -> List[Dict]:
        """Load processed restaurant data"""
        print(f"\n📖 Loading data from: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded {len(data)} restaurants")
        return data
    
    def create_embeddings(self, restaurants: List[Dict]) -> None:
        """
        Create embeddings and store in ChromaDB
        
        Args:
            restaurants: List of restaurant dictionaries
        """
        print(f"\n🔄 Creating embeddings for {len(restaurants)} restaurants...")
        
        # Prepare data
        documents = []
        metadatas = []
        ids = []
        
        for restaurant in tqdm(restaurants, desc="Preparing data"):
            # Use searchable_text field for embedding
            text = restaurant.get('searchable_text', '')
            if not text:
                # Fallback: combine key fields
                text = f"{restaurant.get('name', '')} {restaurant.get('description', '')} {restaurant.get('address', '')}"
            
            documents.append(text)
            
            # Store metadata for retrieval
            metadata = {
                'name': restaurant.get('name', ''),
                'business_type': restaurant.get('business_type', ''),
                'district': restaurant.get('district', ''),
                'price_range': restaurant.get('price_range', ''),
                'phone': restaurant.get('phone', ''),
                'address': restaurant.get('address', ''),
                'url': restaurant.get('url', ''),
                'cuisine_type': ','.join(restaurant.get('cuisine_type', [])),
                'features': ','.join(restaurant.get('features', []))
            }
            metadatas.append(metadata)
            
            # Use restaurant ID
            ids.append(restaurant.get('id', f"rest_{len(ids)}"))
        
        # Create embeddings using sentence-transformers
        print("\n🧮 Generating embeddings with sentence-transformers...")
        embeddings = self.model.encode(
            documents,
            show_progress_bar=True,
            batch_size=32,
            convert_to_numpy=True
        )
        
        # Store in ChromaDB
        print("\n💾 Storing in ChromaDB...")
        
        # ChromaDB has a limit on batch size, so we'll chunk it
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            end_idx = min(i + batch_size, len(documents))
            
            self.collection.add(
                documents=documents[i:end_idx],
                embeddings=embeddings[i:end_idx].tolist(),
                metadatas=metadatas[i:end_idx],
                ids=ids[i:end_idx]
            )
            print(f"  ✅ Stored batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
        
        print(f"\n✅ Successfully created and stored {len(documents)} embeddings!")
        
    def get_stats(self) -> Dict:
        """Get statistics about the collection"""
        count = self.collection.count()
        return {
            'total_documents': count,
            'collection_name': self.collection.name,
            'db_path': str(self.db_path)
        }
    
    def test_search(self, query: str, n_results: int = 5) -> None:
        """
        Test semantic search
        
        Args:
            query: Search query in Vietnamese
            n_results: Number of results to return
        """
        print(f"\n🔍 Testing search with query: '{query}'")
        print(f"📊 Looking for top {n_results} results...\n")
        
        # Create query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results
        )
        
        # Check if results exist
        if not results or not results.get('ids') or not results['ids'][0]:
            print("❌ No results found")
            return
        
        # Display results
        print("=" * 80)
        print("🎯 SEARCH RESULTS")
        print("=" * 80)
        
        ids = results['ids'][0] if results.get('ids') else []
        metadatas_raw = results.get('metadatas')
        distances_raw = results.get('distances')
        metadatas = metadatas_raw[0] if metadatas_raw else []
        distances = distances_raw[0] if distances_raw else []
        
        for i, (doc_id, metadata, distance) in enumerate(zip(ids, metadatas, distances)):
            print(f"\n{i+1}. {metadata['name']}")
            print(f"   📍 Type: {metadata['business_type']}")
            print(f"   🏙️ District: {metadata['district']}")
            print(f"   💰 Price: {metadata['price_range']}")
            print(f"   📞 Phone: {metadata['phone']}")
            print(f"   📏 Similarity Score: {1 - distance:.4f}")
            print(f"   🔗 {metadata['url']}")
        
        print("\n" + "=" * 80)


def main():
    """Main function to create embeddings"""
    
    # Paths
    data_file = Path(__file__).parent.parent.parent / "data" / "processed" / "restaurants_clean.json"
    
    # Create embeddings
    creator = EmbeddingCreator()
    
    # Load data
    restaurants = creator.load_data(str(data_file))
    
    # Create and store embeddings
    creator.create_embeddings(restaurants)
    
    # Show stats
    stats = creator.get_stats()
    print("\n" + "=" * 80)
    print("📊 STATISTICS")
    print("=" * 80)
    print(f"Collection: {stats['collection_name']}")
    print(f"Total documents: {stats['total_documents']}")
    print(f"Database path: {stats['db_path']}")
    print("=" * 80)
    
    # Test search with various queries
    print("\n" + "=" * 80)
    print("🧪 TESTING SEMANTIC SEARCH")
    print("=" * 80)
    
    test_queries = [
        "Nhà hàng Việt Nam bình dân ở Cầu Giấy",
        "Quán karaoke sang trọng",
        "Bar có view đẹp",
        "Nơi ăn tối lãng mạn cho hẹn hò",
        "Quán ăn cho công ty tổ chức tiệc"
    ]
    
    for query in test_queries:
        creator.test_search(query, n_results=3)
        print("\n")


if __name__ == "__main__":
    main()

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import numpy as np
from typing import List, Tuple, Optional
from config.rag_config import RagConfig
import uuid
import time

class QdrantVectorStore:
    """Qdrant-based vector store for similarity search"""
    
    def __init__(self):
        """Initialize Qdrant vector store"""
        self.dimension = RagConfig.VECTOR_DIMENSION
        self.collection_name = RagConfig.QDRANT_COLLECTION_NAME
        self.client = None
        self.texts = []  # Local cache for texts (optional, for compatibility)
        
        # Initialize Qdrant client
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize Qdrant client and create collection if needed"""
        try:
            print(f"Connecting to Qdrant at {RagConfig.QDRANT_URL}...")
            self.client = QdrantClient(
                url=RagConfig.QDRANT_URL,
                api_key=RagConfig.QDRANT_API_KEY,
                timeout=300  # 5 minutes timeout for large uploads
            )
            
            # Check if collection exists, create if not
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                print(f"Creating collection '{self.collection_name}'...")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.dimension,
                        distance=Distance.COSINE
                    )
                )
                print(f"✓ Collection '{self.collection_name}' created successfully!")
            else:
                print(f"✓ Using existing collection '{self.collection_name}'")
                
        except Exception as e:
            print(f"Error initializing Qdrant client: {e}")
            raise
    
    # search vector để hỏi 
    def search(self, query_embedding: np.ndarray, k: int = RagConfig.TOP_K_RESULTS) -> Tuple[List[str], List[float]]:
        """
        Search for similar embeddings in Qdrant
        
        Args:
            query_embedding: query embedding vector
            k: number of top results to return
            
        Returns:
            tuple of (similar_texts, similarity_scores)
        """
        try:
            # Get collection info to check if it has data
            collection_info = self.client.get_collection(collection_name=self.collection_name)
            if collection_info.points_count == 0:
                return [], []
            
            # Convert to list for Qdrant
            query_vector = query_embedding.astype('float32').tolist()
            
            # Search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=k
            )
            
            # Extract texts and scores
            similar_texts = [hit.payload["text"] for hit in search_results]
            similarity_scores = [hit.score for hit in search_results]
            
            return similar_texts, similarity_scores
            
        except Exception as e:
            print(f"Error searching in Qdrant: {e}")
            return [], []
    
    
    def load_index(self, filepath: str = None):
        """
        Load index (for Qdrant, connect to existing collection)
        This method is kept for compatibility with FAISS interface
        
        Returns:
            True if collection exists and has data, False otherwise
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                print(f"Collection '{self.collection_name}' not found in Qdrant")
                return False
            
            # Get collection info
            collection_info = self.client.get_collection(collection_name=self.collection_name)
            points_count = collection_info.points_count
            
            if points_count == 0:
                print(f"Collection '{self.collection_name}' exists but is empty")
                return False
            
            print(f"Connected to Qdrant collection '{self.collection_name}' with {points_count} vectors")
            
            # Skip rebuilding text cache for faster startup
            # Text will be fetched on-demand during search
            print("✓ Index loaded (text cache will be built on-demand for faster startup)")
            
            return True
            
        except Exception as e:
            print(f"Error loading from Qdrant: {e}")
            return False
    
    
    def delete_collection(self):
        """Delete the collection from Qdrant"""
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            print(f"✓ Deleted collection '{self.collection_name}' from Qdrant")
            self.texts = []
            
        except Exception as e:
            print(f"Error deleting collection: {e}")
            raise

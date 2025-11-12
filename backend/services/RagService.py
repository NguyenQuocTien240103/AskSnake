from typing import List, Dict, Any
from rag.embeddings import EmbeddingGenerator
from rag.vector_store import FAISSVectorStore
from rag.qdrant_vector_store import QdrantVectorStore
from rag.llm import GeminiLLM
from rag.document_processor import DocumentProcessor
from rag.reranker import CrossEncoderReranker
from config.rag_config import RagConfig

class RagService:
    """Main RAG Pipeline orchestrator"""
    
    def __init__(self):
        """Initialize all components of the RAG pipeline"""
        print("Initializing RAG Pipeline...")
        
        # Initialize components
        self.embedding_generator = EmbeddingGenerator()
        
        # Choose vector store based on RagConfig
        if RagConfig.USE_QDRANT:
            print("Using Qdrant Cloud as vector store...")
            self.vector_store = QdrantVectorStore()
        else:
            print("Using FAISS as vector store...")
            self.vector_store = FAISSVectorStore()
        
        self.llm = GeminiLLM()
        self.document_processor = DocumentProcessor()
        
        # Initialize re-ranker if enabled
        self.reranker = None
        if RagConfig.USE_RERANKING:
            try:
                print("Initializing cross-encoder re-ranker...")
                self.reranker = CrossEncoderReranker(RagConfig.CROSS_ENCODER_MODEL)
                print("Re-ranker initialized successfully!")
            except Exception as e:
                print(f"Warning: Failed to initialize re-ranker: {e}")
                print("Continuing without re-ranking...")
                RagConfig.USE_RERANKING = False
        
        # Pipeline state
        self.is_indexed = False
        
        print("RAG Pipeline initialized successfully!")
    
    def ingest_documents(self, documents: List[str]) -> Dict[str, Any]:
        """
        Ingest documents into the RAG pipeline
        
        Args:
            documents: List of document texts to ingest
            
        Returns:
            Dictionary with ingestion statistics
        """
        print(f"Starting document ingestion for {len(documents)} documents...")
        
        all_chunks = []
        total_chunks = 0
        
        # Process each document
        for i, document in enumerate(documents):
            print(f"Processing document {i+1}/{len(documents)}...")
            chunks = self.document_processor.process_document(document)
            all_chunks.extend(chunks)
            total_chunks += len(chunks)
        
        print(f"Total chunks created: {total_chunks}")
        
        # Generate embeddings for all chunks
        print("Generating embeddings...")
        embeddings = self.embedding_generator.generate_embeddings(all_chunks)
        
        # Add to vector store
        print("Adding embeddings to vector store...")
        self.vector_store.add_embeddings(embeddings, all_chunks)
        
        # Save the index
        self.vector_store.save_index()
        
        self.is_indexed = True
        
        stats = {
            "total_documents": len(documents),
            "total_chunks": total_chunks,
            "total_embeddings": len(embeddings),
            "vector_store_stats": self.vector_store.get_stats()
        }
        
        print("Document ingestion completed!")
        return stats
    
    def ingest_documents_with_metadata(self,  documents: List[Dict],  name_field: str = "name_vn", metadata_fields: List[str] = None) -> Dict[str, Any]:
        """
        Ingest documents with metadata-level chunking (context prefix)
        
        Args:
            documents: List of document dictionaries with metadata
            name_field: Field name for entity name (e.g., "name_vn", "name_en")
            metadata_fields: List of metadata field names to process
            
        Returns:
            Dictionary with ingestion statistics
        """
        print(f"Starting metadata-level document ingestion for {len(documents)} entities...")
        
        # Process all documents with metadata context
        all_chunks = self.document_processor.process_document_with_metadata(
            documents=documents,
            name_field=name_field,
            metadata_fields=metadata_fields
        )
        
        total_chunks = len(all_chunks)
        print(f"Total chunks created with metadata context: {total_chunks}")
        
        # Generate embeddings for all chunks
        print("Generating embeddings...")
        embeddings = self.embedding_generator.generate_embeddings(all_chunks)
        
        # Add to vector store
        print("Adding embeddings to vector store...")
        self.vector_store.add_embeddings(embeddings, all_chunks)
        
        # Save the index
        self.vector_store.save_index()
        
        self.is_indexed = True
        
        stats = {
            "total_documents": len(documents),
            "total_chunks": total_chunks,
            "total_embeddings": len(embeddings),
            "vector_store_stats": self.vector_store.get_stats(),
            "metadata_fields": metadata_fields
        }
        
        print("Metadata-level document ingestion completed!")
        return stats
    
    def load_existing_index(self) -> bool:
        """
        Load existing vector index from disk
        
        Returns:
            True if index loaded successfully, False otherwise
        """
        print("Attempting to load existing index...")
        success = self.vector_store.load_index()
        if success:
            self.is_indexed = True
            print("Existing index loaded successfully!")
        else:
            print("No existing index found.")
        return success
    
    def query(self, question: str, top_k: int = RagConfig.TOP_K_RESULTS) -> Dict[str, Any]:
        """
        Query the RAG pipeline with optional re-ranking
        
        Args:
            question: User's question
            top_k: Number of top similar chunks to retrieve (overridden if re-ranking is enabled)
            
        Returns:
            Dictionary containing the response and metadata
        """
        if not self.is_indexed:
            return {
                "response": "Error: No documents have been indexed yet. Please ingest documents first.",
                "context": [],
                "similarity_scores": [],
                "error": "No index available"
            }
        
        print(f"Processing query: {question}")
        
        # Generate embedding for the query
        print("Generating query embedding...")
        query_embedding = self.embedding_generator.generate_single_embedding(question)
        
        # Determine how many candidates to retrieve
        retrieval_k = RagConfig.RERANK_TOP_K if RagConfig.USE_RERANKING else top_k
        
        # Search for similar chunks
        print(f"Searching for relevant context (retrieving top {retrieval_k})...")
        similar_texts, similarity_scores = self.vector_store.search(query_embedding, retrieval_k)
        
        if not similar_texts:
            return {
                "response": "I couldn't find any relevant information to answer your question.",
                "context": [],
                "similarity_scores": [],
                "error": "No relevant context found"
            }
        
        print(f"Found {len(similar_texts)} relevant chunks from vector search")
        
        # Apply re-ranking if enabled
        final_texts = similar_texts
        final_scores = similarity_scores
        rerank_info = {}
        
        if RagConfig.USE_RERANKING and self.reranker is not None:
            print("Applying cross-encoder re-ranking...")
            
            # Combine original results
            passages_with_scores = list(zip(similar_texts, similarity_scores))
            
            # Re-rank with combined scoring
            reranked_results = self.reranker.rerank_with_original_scores(
                question, 
                passages_with_scores, 
                alpha=RagConfig.RERANK_ALPHA,
                top_k=RagConfig.FINAL_TOP_K
            )
            
            # Extract re-ranked results
            final_texts = [item[0] for item in reranked_results]
            final_scores = [item[1] for item in reranked_results]  # Combined scores
            
            rerank_info = {
                "reranking_used": True,
                "original_retrieval_count": len(similar_texts),
                "final_count_after_rerank": len(final_texts),
                "cross_encoder_scores": [item[2] for item in reranked_results],
                "original_scores": [item[3] for item in reranked_results],
                "combined_scores": final_scores
            }
            
            print(f"Re-ranking completed. Final {len(final_texts)} passages selected.")
        else:
            # Use original results, but limit to final_top_k
            final_k = RagConfig.FINAL_TOP_K if RagConfig.USE_RERANKING else top_k
            final_texts = final_texts[:final_k]
            final_scores = final_scores[:final_k]
            rerank_info = {"reranking_used": False}
        
        # Generate response using LLM
        print("Generating response...")
        response = self.llm.generate_response(question, final_texts)
        
        result = {
            "response": response,
            "context": final_texts,
            "similarity_scores": final_scores,
            "num_context_chunks": len(final_texts),
            "rerank_info": rerank_info
        }
        
        print("Query processed successfully!")
        return result
    
    def query_with_image(self, snake_name: str, user_question: str = None, top_k: int = RagConfig.TOP_K_RESULTS) -> Dict[str, Any]:
        """
        Query RAG với context từ image recognition
        Tự động tạo prompt phù hợp dựa trên có hay không có câu hỏi từ user
        
        Args:
            snake_name: Tên loài rắn từ image recognition
            user_question: Câu hỏi từ người dùng (optional)
            top_k: Number of top similar chunks to retrieve
            
        Returns:
            Dictionary containing the response and metadata
        """
        # Case 1: Chỉ có ảnh, không có câu hỏi -> Mô tả tổng quan
        if not user_question or user_question.strip() == "":
            search_query = RagConfig.get_snake_description_prompt(snake_name)
            llm_prompt_template = RagConfig.LLM_SNAKE_DESCRIPTION_TEMPLATE
            print(f"🖼️  Image only mode - Using description prompt for: {snake_name}")
        
        # Case 2: Có cả ảnh và câu hỏi -> Trả lời câu hỏi với context về con rắn đó
        else:
            search_query = RagConfig.get_snake_question_prompt(snake_name, user_question)
            llm_prompt_template = RagConfig.LLM_SNAKE_QUESTION_TEMPLATE
            print(f"🖼️💬 Image + Question mode - Question about {snake_name}: {user_question}")
        
        # Query với prompt đã được tạo và LLM template tương ứng
        return self.query_with_custom_prompt(search_query, llm_prompt_template, top_k)
    
    def query_with_custom_prompt(self, question: str, llm_prompt_template: str, top_k: int = RagConfig.TOP_K_RESULTS) -> Dict[str, Any]:
        """
        Query RAG pipeline với custom LLM prompt template
        
        Args:
            question: Search query để tìm context trong vector store
            llm_prompt_template: Template cho LLM với placeholders {context} và {query}
            top_k: Number of top similar chunks to retrieve
            
        Returns:
            Dictionary containing the response and metadata
        """
        if not self.is_indexed:
            return {
                "response": "Error: No documents have been indexed yet. Please ingest documents first.",
                "context": [],
                "similarity_scores": [],
                "error": "No index available"
            }
        
        print(f"Processing query with custom prompt: {question[:100]}...")
        
        # Generate embedding for the query
        print("Generating query embedding...")
        query_embedding = self.embedding_generator.generate_single_embedding(question)
        
        # Determine how many candidates to retrieve
        retrieval_k = RagConfig.RERANK_TOP_K if RagConfig.USE_RERANKING else top_k
        
        # Search for similar chunks
        print(f"Searching for relevant context (retrieving top {retrieval_k})...")
        similar_texts, similarity_scores = self.vector_store.search(query_embedding, retrieval_k)
        
        if not similar_texts:
            return {
                "response": "I couldn't find any relevant information to answer your question.",
                "context": [],
                "similarity_scores": [],
                "error": "No relevant context found"
            }
        
        print(f"Found {len(similar_texts)} relevant chunks from vector search")
        
        # Apply re-ranking if enabled
        final_texts = similar_texts
        final_scores = similarity_scores
        rerank_info = {}
        
        if RagConfig.USE_RERANKING and self.reranker is not None:
            print("Applying cross-encoder re-ranking...")
            passages_with_scores = list(zip(similar_texts, similarity_scores))
            reranked_results = self.reranker.rerank_with_original_scores(
                question, 
                passages_with_scores, 
                alpha=RagConfig.RERANK_ALPHA,
                top_k=RagConfig.FINAL_TOP_K
            )
            
            final_texts = [item[0] for item in reranked_results]
            final_scores = [item[1] for item in reranked_results]
            
            rerank_info = {
                "reranking_used": True,
                "original_retrieval_count": len(similar_texts),
                "final_count_after_rerank": len(final_texts),
                "cross_encoder_scores": [item[2] for item in reranked_results],
                "original_scores": [item[3] for item in reranked_results],
                "combined_scores": final_scores
            }
            
            print(f"Re-ranking completed. Final {len(final_texts)} passages selected.")
        else:
            final_k = RagConfig.FINAL_TOP_K if RagConfig.USE_RERANKING else top_k
            final_texts = final_texts[:final_k]
            final_scores = final_scores[:final_k]
            rerank_info = {"reranking_used": False}
        
        # Generate response using LLM với custom prompt template
        print(f"Generating response with custom prompt template...")
        response = self.llm.generate_response(question, final_texts, custom_prompt_template=llm_prompt_template)
        
        result = {
            "response": response,
            "context": final_texts,
            "similarity_scores": final_scores,
            "num_context_chunks": len(final_texts),
            "rerank_info": rerank_info
        }
        
        print("Query processed successfully!")
        return result
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current pipeline state
        
        Returns:
            Dictionary with pipeline statistics
        """
        rerank_info = {}
        if RagConfig.USE_RERANKING:
            rerank_info = {
                "reranking_enabled": True,
                "cross_encoder_model": RagConfig.CROSS_ENCODER_MODEL,
                "rerank_top_k": RagConfig.RERANK_TOP_K,
                "final_top_k": RagConfig.FINAL_TOP_K,
                "rerank_alpha": RagConfig.RERANK_ALPHA,
                "reranker_loaded": self.reranker is not None
            }
        else:
            rerank_info = {"reranking_enabled": False}
        
        stats = {
            "is_indexed": self.is_indexed,
            "vector_store_stats": self.vector_store.get_stats(),
            "reranking": rerank_info,
            "RagConfig": {
                "chunk_size": RagConfig.CHUNK_SIZE,
                "chunk_overlap": RagConfig.CHUNK_OVERLAP,
                "top_k_results": RagConfig.TOP_K_RESULTS,
                "llm_model": RagConfig.LLM_MODEL,
                "embedding_model": RagConfig.EMBEDDING_MODEL
            }
        }
        return stats
    
    def reset_pipeline(self):
        """Reset the pipeline by clearing the vector store"""
        print("Resetting pipeline...")
        self.vector_store = FAISSVectorStore()
        self.is_indexed = False
        print("Pipeline reset completed!")
    
    def test_components(self) -> Dict[str, bool]:
        """
        Test all pipeline components
        
        Returns:
            Dictionary with test results for each component
        """
        print("Testing pipeline components...")
        
        results = {}
        
        # Test embedding generator
        try:
            test_embedding = self.embedding_generator.generate_single_embedding("Test text")
            results["embedding_generator"] = len(test_embedding) == RagConfig.VECTOR_DIMENSION
            print("✓ Embedding generator test passed")
        except Exception as e:
            results["embedding_generator"] = False
            print(f"✗ Embedding generator test failed: {e}")
        
        # Test LLM
        try:
            test_response = self.llm.generate_simple_response("Hello, how are you?")
            results["llm"] = len(test_response) > 0
            print("✓ LLM test passed")
        except Exception as e:
            results["llm"] = False
            print(f"✗ LLM test failed: {e}")
        
        # Test document processor
        try:
            test_chunks = self.document_processor.process_document("This is a test document. It has multiple sentences. Each sentence should be processed correctly.")
            results["document_processor"] = len(test_chunks) > 0
            print("✓ Document processor test passed")
        except Exception as e:
            results["document_processor"] = False
            print(f"✗ Document processor test failed: {e}")
        
        # Test vector store
        try:
            self.vector_store.create_index()
            results["vector_store"] = self.vector_store.index is not None
            print("✓ Vector store test passed")
        except Exception as e:
            results["vector_store"] = False
            print(f"✗ Vector store test failed: {e}")
        
        print("Component testing completed!")
        return results
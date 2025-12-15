from typing import List, Dict, Any, Optional
from rag.embeddings import EmbeddingGenerator
# from rag.vector_store import FAISSVectorStore
from rag.qdrant_vector_store import QdrantVectorStore
from rag.llm import GeminiLLM
# from rag.document_processor import DocumentProcessor
from rag.reranker import CrossEncoderReranker
from config.rag_config import RagConfig

class RagService:
    """Main RAG Pipeline orchestrator"""
    
    def __init__(self):
        """Initialize all components of the RAG pipeline"""
        print("Initializing RAG Pipeline...")
        
        # Initialize components
        self.embedding_generator = EmbeddingGenerator()
        
        if RagConfig.USE_QDRANT:
            self.vector_store = QdrantVectorStore()

        self.llm = GeminiLLM()
        # self.document_processor = DocumentProcessor()
        
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
    
    def query(self, question: str, top_k: int = RagConfig.TOP_K_RESULTS,chat_history: List[Dict[str, Any]] = None,summary: Optional[str] = None) -> Dict[str, Any]:
        """
        Query the RAG pipeline with optional re-ranking and chat history
        
        Args:
            question: User's question
            top_k: Number of top similar chunks to retrieve (overridden if re-ranking is enabled)
            chat_history: Chat history for context-aware responses (optional)
            summary: Conversation summary (optional)
            
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
        
        # Generate response using LLM (with or without history)
        print("Generating response...")
        if chat_history:
            # Use history-aware generation
            response = self.llm.generate_response_with_history(
                query=question,
                context=final_texts,
                chat_history=chat_history,
                summary=summary
            )
        else:
            # Standard generation without history
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
    
    def query_with_image(self, snake_name: str, user_question: str = None, top_k: int = RagConfig.TOP_K_RESULTS,chat_history: List[Dict[str, Any]] = None,summary: Optional[str] = None) -> Dict[str, Any]:
        """
        Query RAG với context từ image recognition + chat history
        Tự động tạo prompt phù hợp dựa trên có hay không có câu hỏi từ user
        
        Args:
            snake_name: Tên loài rắn từ image recognition
            user_question: Câu hỏi từ người dùng (optional)
            top_k: Number of top similar chunks to retrieve
            chat_history: Chat history for context-aware responses (optional)
            summary: Conversation summary (optional)
            
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
        
        # Query với prompt đã được tạo, LLM template tương ứng, VÀ history
        return self.query_with_custom_prompt(
            question=search_query, 
            llm_prompt_template=llm_prompt_template, 
            top_k=top_k,
            chat_history=chat_history,
            summary=summary
        )
    
    def query_with_custom_prompt(self, question: str, llm_prompt_template: str, top_k: int = RagConfig.TOP_K_RESULTS,chat_history: List[Dict[str, Any]] = None,summary: Optional[str] = None) -> Dict[str, Any]:
        """
        Query RAG pipeline với custom LLM prompt template + chat history
        
        Args:
            question: Search query để tìm context trong vector store
            llm_prompt_template: Template cho LLM với placeholders {context} và {query}
            top_k: Number of top similar chunks to retrieve
            chat_history: Chat history for context-aware responses (optional)
            summary: Conversation summary (optional)
            
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
        
        # Generate response using LLM với custom prompt template (with or without history)
        print(f"Generating response with custom prompt template...")
        
        if chat_history:
            # Use history-aware generation with custom template
            response = self.llm.generate_response_with_history(
                query=question,
                context=final_texts,
                chat_history=chat_history,
                summary=summary,
                custom_prompt_template=llm_prompt_template
            )
        else:
            # Standard generation with custom template
            response = self.llm.generate_response(
                question=question, 
                context_texts=final_texts, 
                custom_prompt_template=llm_prompt_template
            )
        
        result = {
            "response": response,
            "context": final_texts,
            "similarity_scores": final_scores,
            "num_context_chunks": len(final_texts),
            "rerank_info": rerank_info
        }
        
        print("Query processed successfully!")
        return result
    
    
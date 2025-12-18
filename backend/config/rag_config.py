import os
from dotenv import load_dotenv

load_dotenv()

class RagConfig:
    """Configuration class for RAG pipeline"""
    
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    
    # Model configurations
    LLM_MODEL = "gemini-2.5-flash"
    EMBEDDING_MODEL = "intfloat/multilingual-e5-small"  # Local embedding model (384 dimensions)
    EMBEDDING_BATCH_SIZE = 32  # Batch size for local model (adjust based on your GPU/CPU)
    EMBEDDING_DELAY = 0  # No delay needed for local model
    
    # LLM Rate limiting (Gemini Free Tier: 10 requests/minute)
    LLM_REQUESTS_PER_MINUTE = 9  # Stay under 10 to be safe
    LLM_DELAY_BETWEEN_REQUESTS = 7  # Delay in seconds (60/9 ≈ 6.7s)
    
    # RAG configurations
    TOP_K_RESULTS = 5  # Legacy parameter (không dùng nếu có reranking)
    
    # Re-ranking configurations
    USE_RERANKING = True
    CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-12-v2"
    
    # Với chunk size lớn (110-300 words), mỗi chunk chứa nhiều thông tin
    # → Cần ít chunks hơn để đủ context
    RERANK_TOP_K = 15   # Lấy 15 candidates để rerank (tăng từ 10)
    FINAL_TOP_K = 5     # Giữ top 5 chunks có điểm cao nhất sau rerank
    
    # Giải thích:
    # - RERANK_TOP_K = 15: Đủ rộng để cover nhiều fields khác nhau
    # - FINAL_TOP_K = 5: 5 chunks × 150-300 words = 750-1500 words context
    #   → Đủ để trả lời hầu hết câu hỏi mà không quá dài
    # - Nếu câu hỏi phức tạp: có thể tăng FINAL_TOP_K lên 8-10
    
    RERANK_ALPHA = 0.7  # Weight for cross-encoder score (0.7) vs original score (0.3)
    
    # FAISS configurations
    VECTOR_DIMENSION = 384  # multilingual-e5-small embedding dimension
    FAISS_INDEX_PATH = "faiss_index"
    
    # Qdrant configurations 
    USE_QDRANT = True  # Set to True to use Qdrant instead of FAISS (tạm thời dùng FAISS vì mạng không ổn)
    QDRANT_COLLECTION_NAME = "snake_knowledge_base" # Lưu trữ trong Qdrant
    
    # Prompt templates cho image recognition
    
    # Prompt 1: Chỉ có ảnh, không có câu hỏi -> Mô tả tổng quan
    SNAKE_DESCRIPTION_PROMPT = (
        "Hãy mô tả chi tiết về loài rắn {snake_name}. "
        "Bao gồm các thông tin sau:\n"
        "1. Đặc điểm nhận dạng (màu sắc, hình dáng, kích thước)\n"
        "2. Môi trường sống và phân bố địa lý\n"
        "3. Mức độ nguy hiểm (có độc hay không, độc tính)\n"
    )
    
    # Prompt 2: Có cả ảnh và câu hỏi -> Trả lời câu hỏi cụ thể
    SNAKE_QUESTION_PROMPT = (
        "Đây là loài rắn {snake_name}.\n"
        "Câu hỏi của người dùng: {user_question}\n\n"
        "Hãy trả lời câu hỏi trên dựa trên thông tin về loài rắn {snake_name}. "
        "Nếu câu hỏi liên quan đến các khía cạnh khác (như so sánh, phân loại, v.v.), "
        "hãy cung cấp thông tin phù hợp và chính xác."
    )
    
    # LLM Prompt Templates (để pass vào LLM.generate_response())
    
    # Template cho mô tả tổng quan về rắn
    LLM_SNAKE_DESCRIPTION_TEMPLATE = """# Vai trò:
                                            Hãy trả lời như một chuyên gia về rắn thực thụ, với văn phong khoa học, tự nhiên và chuyên nghiệp. 
                                            Không được phép trả lời là dựa vào thông tin ngữ cảnh hay ngữ cảnh được cung cấp mà phải trả lời như một chuyên gia thực thụ mà không dựa vào bất cứ điều gì .

                                        # Thông tin ngữ cảnh:
                                            {context}

                                        # Câu hỏi:
                                            {query}

                                        # Yêu cầu:
                                            - Chỉ sử dụng thông tin có trong phần "Thông tin ngữ cảnh" và ĐẶC BIỆT không được 
                                            trả lời là theo ngữ cảnh được cung cấp mà phải trả lời như mình là 1 chuyên gia thực thụ.
                                            - Không suy đoán hoặc bổ sung kiến thức bên ngoài ngữ cảnh.

                                        # Yêu cầu định dạng:
                                            - Tuyệt đối KHÔNG sử dụng ký hiệu markdown như ##, ### hoặc dấu * để định dạng tiêu đề.
                                            - Tuyệt đối KHÔNG sử dụng ký hiệu ** ** để bọc tên rắn.
                                            - Tên khoa học của rắn được viết hoa chữ cái đầu và in đậm.
                                            - Tên thông dụng tiếng Việt được viết ngay sau tên khoa học. Ví dụ: Bungarus fasciatus (Rắn cạp nống).
                                            - Chia nội dung thành các phần được đánh số (1, 2, 3, ...).
                                            - Sử dụng các đoạn văn ngắn, ngắt dòng rõ ràng.
                                            - Văn phong khoa học, giống như một nhà nghiên cứu viết trong tài liệu Word.

                                        # Kết thúc:
                                            Ở cuối câu trả lời, hãy đề xuất 3–5 câu hỏi liên quan (dạng gạch đầu dòng) 
                                            để người đọc có thể tìm hiểu sâu hơn về loài rắn này, 
                                            sau đó mời người dùng chọn một câu hỏi để tiếp tục.

                                        # Ví dụ mẫu trả lời:

                                            Bungarus fasciatus (Rắn cạp nia bắc)

                                            1. Đặc điểm nhận dạng (màu sắc, hình dáng, kích thước)  
                                            Bungarus fasciatus có thân hình tròn, kích thước trung bình đến lớn.  
                                            Màu sắc đặc trưng gồm các khoang màu đen và vàng xen kẽ rõ ràng dọc theo chiều dài cơ thể.  
                                            Đầu nhỏ, không phân biệt rõ với cổ, mắt nhỏ, phù hợp với tập tính hoạt động về đêm.

                                            2. Môi trường sống và phân bố địa lý  
                                            Theo thông tin trong ngữ cảnh, loài này phân bố tại một số khu vực thuộc Đông Nam Á.  
                                            Rắn thường được ghi nhận trong các khu rừng thưa, rìa rừng và các khu vực gần nơi cư trú của con người.  
                                            Một số chi tiết về sinh cảnh cụ thể chưa được mô tả đầy đủ trong dữ liệu hiện có.

                                            3. Mức độ nguy hiểm (có độc hay không, độc tính)  
                                            Bungarus fasciatus là loài rắn có nọc độc thần kinh mạnh.  
                                            Nọc độc có thể gây liệt cơ và suy hô hấp nếu không được điều trị kịp thời.  

                                            Câu hỏi gợi ý để bạn tìm hiểu thêm về Bungarus fasciatus:
                                            - ...
                                            - ...

                                        """

    # Template cho trả lời câu hỏi cụ thể về rắn
    LLM_SNAKE_QUESTION_TEMPLATE = """   # Vai trò:
                                            Hãy trả lời như một chuyên gia về rắn thực thụ, với văn phong khoa học, tự nhiên và chuyên nghiệp. 
                                            Không được phép trả lời là dựa vào thông tin ngữ cảnh hay ngữ cảnh được cung cấp mà phải trả lời như một chuyên gia thực thụ mà không dựa vào bất cứ điều gì .

                                        # Thông tin ngữ cảnh:
                                            {context}

                                        # Câu hỏi:
                                            {query}

                                        # Yêu cầu:
                                            - Chỉ sử dụng thông tin có trong phần "Thông tin ngữ cảnh" và ĐẶC BIỆT không được 
                                            trả lời là theo ngữ cảnh được cung cấp mà phải trả lời như mình là 1 chuyên gia thực thụ.
                                            - Không suy đoán hoặc bổ sung kiến thức bên ngoài ngữ cảnh.

                                        # Yêu cầu định dạng:
                                            - Tuyệt đối KHÔNG sử dụng ký hiệu markdown như ##, ### hoặc dấu * để định dạng tiêu đề.
                                            - Tuyệt đối KHÔNG sử dụng ký hiệu ** ** để bọc tên rắn.
                                            - Tên khoa học của rắn được viết hoa chữ cái đầu và in đậm. Ví dụ: Bungarus fasciatus (Rắn cạp nống).
                                            - Tên thông dụng tiếng Việt được viết ngay sau tên khoa học.
                                            - Chia nội dung thành các phần được đánh số (1, 2, 3, ...).
                                            - Sử dụng các đoạn văn ngắn, ngắt dòng rõ ràng.
                                            - Văn phong khoa học, giống như một nhà nghiên cứu viết trong tài liệu Word.

                                        # Kết thúc:
                                            Ở cuối câu trả lời, hãy đề xuất 3–5 câu hỏi liên quan (dạng gạch đầu dòng) 
                                            để người đọc có thể tìm hiểu sâu hơn về loài rắn này, 
                                            sau đó mời người dùng chọn một câu hỏi để tiếp tục.
                                            Với cấu trúc câu hỏi bao gồm nội dung chính như sau : 
                                                - Tên khoa học và tên thông thường
                                                - Phân loại học tập
                                                - Cấu hình đặc biệt
                                                - Độc tính
                                                - Hành vi săn bắn
                                                - Hành vi và sinh thái học
                                                - Phân vùng địa lý và môi trường sống
                                                - Sinh sản
                                                - Bảo tồn trạng thái
                                                - Nghiên cứu có giá trị
                                                - Ý nghĩa đối với con người
                                                - Triệu chứng khi đã sẵn sàng
                                                - Xử lý như thế nào

                                         # Ví dụ mẫu trả lời:

                                            Bungarus fasciatus (Rắn cạp nia bắc)

                                            1. Đặc điểm nhận dạng (màu sắc, hình dáng, kích thước)  
                                            Bungarus fasciatus có thân hình tròn, kích thước trung bình đến lớn.  
                                            Màu sắc đặc trưng gồm các khoang màu đen và vàng xen kẽ rõ ràng dọc theo chiều dài cơ thể.  
                                            Đầu nhỏ, không phân biệt rõ với cổ, mắt nhỏ, phù hợp với tập tính hoạt động về đêm.

                                            2. Môi trường sống và phân bố địa lý  
                                            Theo thông tin trong ngữ cảnh, loài này phân bố tại một số khu vực thuộc Đông Nam Á.  
                                            Rắn thường được ghi nhận trong các khu rừng thưa, rìa rừng và các khu vực gần nơi cư trú của con người.  
                                            Một số chi tiết về sinh cảnh cụ thể chưa được mô tả đầy đủ trong dữ liệu hiện có.

                                            3. Mức độ nguy hiểm (có độc hay không, độc tính)  
                                            Bungarus fasciatus là loài rắn có nọc độc thần kinh mạnh.  
                                            Nọc độc có thể gây liệt cơ và suy hô hấp nếu không được điều trị kịp thời.  

                                            Câu hỏi gợi ý để bạn tìm hiểu thêm về Bungarus fasciatus:
                                            - ...
                                            - ...
                                            """
    
    @classmethod
    def get_snake_description_prompt(cls, snake_name: str) -> str:
        """
        Generate prompt for full snake description (when only image is provided)
        
        Args:
            snake_name: Name of the snake species
            
        Returns:
            Formatted prompt for general description
        """
        return cls.SNAKE_DESCRIPTION_PROMPT.format(snake_name=snake_name)
    
    @classmethod
    def get_snake_question_prompt(cls, snake_name: str, user_question: str) -> str:
        """
        Generate prompt for answering specific question about the snake
        
        Args:
            snake_name: Name of the snake species
            user_question: User's specific question
            
        Returns:
            Formatted prompt for answering the question with context
        """
        return cls.SNAKE_QUESTION_PROMPT.format(
            snake_name=snake_name,
            user_question=user_question
        )
    
    @classmethod
    def validate(cls):
        """Validate that all required configurations are set"""
        # Only validate Google API key for LLM (embedding now runs locally)
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment variables (needed for LLM)")
        if cls.USE_QDRANT and not cls.QDRANT_API_KEY:
            raise ValueError("QDRANT_API_KEY not found in environment variables")
        return True
from google import genai
from google.genai import types
from config.rag_config import RagConfig
from typing import List, Dict

class GeminiLLM:
    """Gemini 2.5 Flash LLM for generating responses"""
    
    def __init__(self):
        """Initialize Gemini LLM client"""
        RagConfig.validate()
        self.client = genai.Client(api_key=RagConfig.GOOGLE_API_KEY)
        self.model = RagConfig.LLM_MODEL
    
    def generate_response(self, query: str, context: List[str], custom_prompt_template: str = None) -> str:
        """
        Generate response using query and retrieved context
        
        Args:
            query: User's question
            context: List of relevant text chunks from vector search
            custom_prompt_template: Custom prompt template with {context} and {query} placeholders
            
        Returns:
            Generated response string
        """
        # Prepare context
        context_text = "\n\n".join([f"Context {i+1}: {text}" for i, text in enumerate(context)])
        
        # Use custom prompt if provided, otherwise use default
        if custom_prompt_template:
            prompt = custom_prompt_template.format(context=context_text, query=query)
        else:
            # Default prompt
            prompt = f"""# Vai trò:
                            Hãy trả lời như một chuyên gia về rắn thực thụ, với văn phong khoa học, tự nhiên và chuyên nghiệp. 
                            .Hãy sử dụng thông tin ngữ cảnh để trả lời câu hỏi của người dùng một cách tự nhiên và chuyên nghiệp.

                        # Thông tin ngữ cảnh:
                            {context}

                        # Câu hỏi:
                            {query}

                        # Yêu cầu:
                            - Không được phép trả lời là dựa vào thông tin ngữ cảnh hay thông tin này hay thông tin kia mà phải trả lời như một chuyên gia thực thụ.
                            - Chỉ sử dụng thông tin có trong phần "Thông tin ngữ cảnh".
                            - Không suy đoán hoặc bổ sung kiến thức bên ngoài ngữ cảnh.
                            - Nếu ngữ cảnh không đủ để trả lời đầy đủ, hãy nêu rõ giới hạn thông tin.

                        # Yêu cầu định dạng:
                            - Không sử dụng ký hiệu markdown như ##, ### hoặc dấu * để định dạng tiêu đề.
                            - Không sử dụng ký hiệu ** ** để bọc tên rắn.
                            - Tên khoa học của rắn được viết hoa chữ cái đầu và in đậm.
                            - Tên thông dụng tiếng Việt được viết ngay sau tên khoa học. Ví dụ: Bungarus fasciatus (Rắn cạp nống).
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

        try:
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ]
            
            # Configure generation with thinking disabled
            generate_content_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_budget=0,
                ),
            )
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=generate_content_config
            )
            
            final_response = response.candidates[0].content.parts[0].text
            return final_response
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"Sorry, I encountered an error while generating the response: {str(e)}"
    
    
    def generate_response_with_history(
        self, 
        query: str, 
        context: List[str], 
        chat_history: List[Dict[str, str]], 
        summary: str = None,
        custom_prompt_template: str = None
    ) -> str:
        """
        Generate response với chat history và summary
        
        Args:
            query: Câu hỏi hiện tại
            context: Context từ RAG
            chat_history: 10 messages gần nhất [{"role": "human/ai", "content": "..."}]
            summary: Tóm tắt cuộc hội thoại (nếu có)
            custom_prompt_template: Custom prompt template (optional, overrides default)
            
        Returns:
            Generated response
        """
        # Chuẩn bị context từ RAG
        context_text = "\n\n".join([f"Context {i+1}: {text}" for i, text in enumerate(context)])
        
        # Chuẩn bị chat history
        history_text = ""
        if chat_history:
            history_lines = []
            for msg in chat_history:
                role = "User" if msg["role"] == "human" else "Assistant"
                history_lines.append(f"{role}: {msg['content']}")
            history_text = "\n".join(history_lines)
        
        # Chuẩn bị summary
        summary_text = f"\n\nConversation Summary:\n{summary}" if summary else ""
        
        # Build prompt - use custom template if provided
        if custom_prompt_template:
            # Custom template với history
            prompt = f""" # Vai trò:
                            Hãy trả lời như một chuyên gia về rắn thực thụ, với văn phong khoa học, tự nhiên và chuyên nghiệp. 
                            .Hãy sử dụng thông tin ngữ cảnh và lịch sử trò chuyện để trả lời câu hỏi của người dùng một cách tự nhiên và chuyên nghiệp.

                            {summary_text}

                            # Lịch sử trò chuyện gần đây:
                            {history_text if history_text else "(Không có tin nhắn trước đó)"}

                            {custom_prompt_template.format(context=context_text, query=query)}
                            """
        else:
            # Default template
            prompt = f"""   # Vai trò:
                            Hãy trả lời như một chuyên gia về rắn thực thụ, với văn phong khoa học, tự nhiên và chuyên nghiệp. 
                            .Hãy sử dụng thông tin ngữ cảnh và lịch sử trò chuyện để trả lời câu hỏi của người dùng một cách tự nhiên và chuyên nghiệp.

                            {summary_text}

                            Lịch sử trò chuyện gần đây:

                            {history_text if history_text else "(Không có tin nhắn trước đó)"}

                            Thông tin ngữ cảnh từ cơ sở kiến ​​thức:

                            {context_text}

                            Câu hỏi hiện tại: {query}

                            # Yêu cầu:
                                - Không được phép trả lời là dựa vào thông tin ngữ cảnh hay thông tin này hay thông tin kia mà phải trả lời như một chuyên gia thực thụ.
                                - Chỉ sử dụng thông tin có trong phần "Thông tin ngữ cảnh".
                                - Không suy đoán hoặc bổ sung kiến thức bên ngoài ngữ cảnh.
                                - Nếu ngữ cảnh không đủ để trả lời đầy đủ, hãy nêu rõ giới hạn thông tin.

                            # Yêu cầu định dạng:
                                - Không sử dụng ký hiệu markdown như ##, ### hoặc dấu * để định dạng tiêu đề.
                                - Không sử dụng ký hiệu ** ** để bọc tên rắn.
                                - Tên khoa học của rắn được viết hoa chữ cái đầu và in đậm.
                                - Tên thông dụng tiếng Việt được viết ngay sau tên khoa học.Ví dụ: Bungarus fasciatus (Rắn cạp nống).
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

        try:
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ]
            
            generate_content_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_budget=0,
                ),
            )
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=generate_content_config
            )
            
            return response.candidates[0].content.parts[0].text
            
        except Exception as e:
            print(f"Error generating response with history: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def generate_summary(self, messages: List[Dict[str, str]]) -> str:
        """
        Tạo tóm tắt cho cuộc hội thoại
        
        Args:
            messages: Danh sách messages [{"role": "human/ai", "content": "..."}]
            
        Returns:
            Tóm tắt cuộc hội thoại
        """
        # Chuẩn bị conversation text
        conversation_lines = []
        for msg in messages:
            role = "User" if msg["role"] == "human" else "Assistant"
            conversation_lines.append(f"{role}: {msg['content']}")
        
        conversation_text = "\n".join(conversation_lines)
        
        prompt = f"""Hãy tóm tắt ngắn gọn cuộc hội thoại sau đây về loài rắn.Tập ​​trung vào các chủ đề chính được thảo luận,
                    các câu hỏi quan trọng được đặt ra và thông tin quan trọng được cung cấp.Giữ bản tóm tắt dưới 200 từ.

                    Conversation:
                    {conversation_text}

                    Summary:"""

        try:
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ]
            
            generate_content_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_budget=0,
                ),
            )
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=generate_content_config
            )
            
            return response.candidates[0].content.parts[0].text
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "Error generating summary."

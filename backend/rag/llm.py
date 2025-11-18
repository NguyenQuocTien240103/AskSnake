# from google import genai
# from google.genai import types
# from config.rag_config import RagConfig
# from typing import List

# class GeminiLLM:
#     """Gemini 2.5 Flash LLM for generating responses"""
    
#     def __init__(self):
#         """Initialize Gemini LLM client"""
#         RagConfig.validate()
#         self.client = genai.Client(api_key=RagConfig.GOOGLE_API_KEY)
#         self.model = RagConfig.LLM_MODEL
    
#     def generate_response(self, query: str, context: List[str]) -> str:
#         """
#         Generate response using query and retrieved context
        
#         Args:
#             query: User's question
#             context: List of relevant text chunks from vector search
            
#         Returns:
#             Generated response string
#         """
#         # Prepare context
#         context_text = "\n\n".join([f"Context {i+1}: {text}" for i, text in enumerate(context)])
        
#         # Create prompt
#         prompt = f"""Consider yourself a snake expert to give professional answers, answer users like an expert and not answer like you rely on this or that information to give results even though you have to get results from context to answer

# Based on the following context information, please answer the question accurately and comprehensively.

# Context Information: (But when answering, don't write that it is based on any context.)
# {context_text}

# Question: {query}

# Please provide a detailed answer based on the context provided. If the context doesn't contain enough information to answer the question, please mention that.

# Position yourself as a snake expert, give the user some more questions related to the current question so the user can build on that and then continue saying what question you want me to help you answer"""

#         try:
#             contents = [
#                 types.Content(
#                     role="user",
#                     parts=[
#                         types.Part.from_text(text=prompt),
#                     ],
#                 ),
#             ]
            
#             # Configure generation with thinking disabled
#             generate_content_config = types.GenerateContentConfig(
#                 thinking_config=types.ThinkingConfig(
#                     thinking_budget=0,
#                 ),
#             )
            
#             response = self.client.models.generate_content(
#                 model=self.model,
#                 contents=contents,
#                 config=generate_content_config
#             )
            
#             final_response = response.candidates[0].content.parts[0].text
#             return final_response
            
#         except Exception as e:
#             print(f"Error generating response: {e}")
#             return f"Sorry, I encountered an error while generating the response: {str(e)}"
    
#     def generate_simple_response(self, text: str) -> str:
#         """
#         Generate a simple response without context (for testing)
        
#         Args:
#             text: Input text
            
#         Returns:
#             Generated response string
#         """
#         try:
#             contents = [
#                 types.Content(
#                     role="user",
#                     parts=[
#                         types.Part.from_text(text=text),
#                     ],
#                 ),
#             ]
            
#             generate_content_config = types.GenerateContentConfig(
#                 thinking_config=types.ThinkingConfig(
#                     thinking_budget=0,
#                 ),
#             )
            
#             response = self.client.models.generate_content(
#                 model=self.model,
#                 contents=contents,
#                 config=generate_content_config
#             )
            
#             final_response = response.candidates[0].content.parts[0].text
#             return final_response
            
#         except Exception as e:
#             print(f"Error generating simple response: {e}")
#             return f"Sorry, I encountered an error: {str(e)}"





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
            prompt = f"""Consider yourself a snake expert to give professional answers, answer users like an expert and not answer like you rely on this or that information to give results even though you have to get results from context to answer

Based on the following context information, please answer the question accurately and comprehensively.

Context Information: (But when answering, don't write that it is based on any context.)
{context_text}

Question: {query}

Please provide a detailed answer based on the context provided. If the context doesn't contain enough information to answer the question, please mention that.

Position yourself as a snake expert, give the user some more questions related to the current question so the user can build on that and then continue saying what question you want me to help you answer

With the question structure including the main content as follows, 3 to 5 questions can be randomly given to users for reference.
-Scientific name and common name
-Taxonomy
-Morphological characteristics
-Toxicology
-Predation behavior
-Behavior and ecology
-Geographic distribution and habitat
-Reproduction
-Conservation status
-Research value
-Human relevance
-Symptoms when bitten
-How to handle"""

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
    
    def generate_simple_response(self, text: str) -> str:
        """
        Generate a simple response without context (for testing)
        
        Args:
            text: Input text
            
        Returns:
            Generated response string
        """
        try:
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=text),
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
            
            final_response = response.candidates[0].content.parts[0].text
            return final_response
            
        except Exception as e:
            print(f"Error generating simple response: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
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
            prompt = f"""You are a snake expert assistant. Use the context information and chat history to answer the user's question.

{summary_text}

Recent Chat History:
{history_text if history_text else "(No previous messages)"}

{custom_prompt_template.format(context=context_text, query=query)}"""
        else:
            # Default template
            prompt = f"""You are a snake expert assistant. Use the context information and chat history to answer the user's question naturally and professionally.

{summary_text}

Recent Chat History:
{history_text if history_text else "(No previous messages)"}

Context Information from Knowledge Base:
{context_text}

Current Question: {query}

Instructions:
- Answer naturally as an expert without mentioning "based on context" or "according to the information"
- Consider the chat history to provide contextually relevant responses
- If the question refers to previous messages, use that context appropriately
- Suggest 3-5 related questions the user might want to explore
- Format your response clearly with appropriate sections

Response:"""

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
        
        prompt = f"""Please provide a concise summary of the following conversation about snakes. 
Focus on the main topics discussed, key questions asked, and important information provided.
Keep the summary under 200 words.

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

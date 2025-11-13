"""
Chat Router - Xử lý luồng chat với RAG và MongoDB
Luồng:
1. Lưu message user vào MongoDB (role=human)
2. Lấy 10 messages gần nhất + summary từ MongoDB
3. RAG: lấy thông tin liên quan từ Qdrant
4. Ghép prompt + context + history → LLM
5. Lưu phản hồi vào MongoDB (role=ai)
6. Tự động tóm tắt nếu hội thoại dài (>20 messages)
"""
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from typing import Optional
from pydantics.chat import ChatRequest, ChatResponse
from services.ChatService import ChatService
from services.RagService import RagService
from services.ImageService import ImageService
from config.rag_config import RagConfig

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Initialize services
chat_service = ChatService()
rag_service = RagService()
image_service = ImageService()

# Load existing RAG index
if not rag_service.load_existing_index():
    print("Warning: No existing RAG index found.")

# Cấu hình
MAX_MESSAGES_BEFORE_SUMMARY = 4  # Tự động tóm tắt sau 4 messages (2 turns: user + AI)
RECENT_MESSAGES_COUNT = 3  # Lấy 3 messages gần nhất (giảm để tiết kiệm context)


@router.post("/message", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def send_message(
    user_id: str = Form(...),
    message: Optional[str] = Form(None),  # ✅ Made optional for image-only requests
    chat_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Gửi message và nhận phản hồi từ AI
    
    Hỗ trợ 3 trường hợp:
    1. Chỉ gửi text (file=None) -> RAG query thông thường
    2. Gửi text + ảnh (file + message) -> Image detection + RAG với câu hỏi cụ thể
    3. Chỉ gửi ảnh (file, message=None) -> Image detection + RAG mô tả tổng quan
    
    Luồng:
    1. Validate input (phải có ít nhất message HOẶC file)
    2. Xử lý image nếu có (detect snake)
    3. Tạo chat mới nếu chưa có chat_id
    4. Lưu message user vào MongoDB (role=human)
    5. Lấy 10 messages gần nhất + summary
    6. Query RAG để lấy context từ Qdrant
    7. LLM generate response với context + history
    8. Lưu response vào MongoDB (role=ai)
    9. Kiểm tra và tự động tóm tắt nếu cần
    """
    try:
        # === VALIDATION: Phải có ít nhất message HOẶC file ===
        if not message and not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You must provide either a message or a file."
            )
        
        snake_name = None
        metadata = {}
        user_message_content = message or ""  # Default to empty string if only image
        
        # === STEP 1: Xử lý image nếu có ===
        if file:
            print(f"📸 Processing uploaded image...")
            file_bytes = await file.read()
            detection_result = await image_service.detect_image(file_bytes)
            snake_name = detection_result["predicted_class"]
            metadata["snake_detected"] = snake_name
            metadata["probability"] = detection_result["probability"]
            print(f"✅ Detected snake: {snake_name} (confidence: {detection_result['probability']:.2%})")
            
            # Nếu chỉ có ảnh không có text -> set default message
            if not message:
                user_message_content = f"[Uploaded image of {snake_name}]"
                print(f"📝 Image-only mode: Auto-generated message for storage")
        
        # === STEP 2: Tạo chat mới nếu chưa có ===
        if not chat_id:
            title = f"Chat về {snake_name}" if snake_name else "New Chat"
            chat_id = await chat_service.create_chat(user_id=user_id, title=title)
            print(f"✅ Created new chat: {chat_id}")
        else:
            # Verify chat exists
            existing_chat = await chat_service.get_chat(chat_id)
            if not existing_chat:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat not found"
                )
        
        # === STEP 3: Lưu message của user vào MongoDB (role=human) ===
        print(f"💾 Saving user message to MongoDB...")
        success = await chat_service.add_message(
            chat_id=chat_id,
            role="human",
            content=user_message_content,
            metadata=metadata
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save user message"
            )
        
        # === STEP 4: Lấy 10 messages gần nhất + summary từ MongoDB ===
        print(f"📚 Fetching recent chat history...")
        recent_messages = await chat_service.get_recent_messages(
            chat_id=chat_id, 
            limit=RECENT_MESSAGES_COUNT
        )
        
        summary = await chat_service.get_chat_summary(chat_id)
        
        print(f"📝 Retrieved {len(recent_messages)} recent messages")
        if summary:
            print(f"📋 Found existing summary: {summary[:100]}...")
        
        # Log chi tiết history để debug
        print(f"\n🔍 DEBUG - Chat History Being Used:")
        for i, msg in enumerate(recent_messages, 1):
            role_emoji = "👤" if msg["role"] == "human" else "🤖"
            print(f"  {i}. {role_emoji} [{msg['role']}]: {msg['content'][:80]}...")
        print()
        
        # === STEP 5: Query RAG để lấy context từ Qdrant ===
        print(f"🔍 Querying RAG for relevant context...")
        
        # Case 1: Có ảnh (với hoặc không có câu hỏi)
        if snake_name:
            print(f"🖼️  Image detected: {snake_name}")
            if message:
                print(f"💬 User question: {message}")
            else:
                print(f"📝 No specific question - will provide general description")
            
            rag_result = rag_service.query_with_image(
                snake_name=snake_name,
                user_question=message,  # None if image-only
                top_k=RagConfig.TOP_K_RESULTS,
                chat_history=recent_messages,
                summary=summary
            )
        # Case 2: Chỉ có text (không có ảnh)
        else:
            print(f"💬 Text-only query: {message}")
            rag_result = rag_service.query(
                question=message,
                top_k=RagConfig.TOP_K_RESULTS,
                chat_history=recent_messages,
                summary=summary
            )
        
        if "error" in rag_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"RAG query failed: {rag_result['error']}"
            )
        
        ai_response = rag_result["response"]
        context_used = rag_result.get("num_context_chunks", 0)
        
        print(f"✅ RAG response generated (used {context_used} context chunks)")
        
        # === STEP 6: Lưu response của AI vào MongoDB (role=ai) ===
        print(f"💾 Saving AI response to MongoDB...")
        ai_metadata = {
            "context_chunks_used": context_used,
            "reranking_used": rag_result.get("rerank_info", {}).get("reranking_used", False)
        }
        
        success = await chat_service.add_message(
            chat_id=chat_id,
            role="ai",
            content=ai_response,
            metadata=ai_metadata
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save AI response"
            )
        
        # === STEP 7: Kiểm tra và tự động tóm tắt nếu cần ===
        was_summarized = False
        total_messages = await chat_service.get_message_count(chat_id)
        
        print(f"📊 Total messages in chat: {total_messages}")
        
        if total_messages >= MAX_MESSAGES_BEFORE_SUMMARY and not summary:
            print(f"📝 Chat has {total_messages} messages, generating summary...")
            
            # Lấy toàn bộ messages để tóm tắt
            all_messages = await chat_service.get_recent_messages(
                chat_id=chat_id,
                limit=total_messages
            )
            
            # Generate summary bằng LLM
            summary_text = rag_service.llm.generate_summary(all_messages)
            
            # Lưu summary vào MongoDB
            await chat_service.update_summary(chat_id, summary_text)
            was_summarized = True
            print(f"✅ Summary generated and saved: {summary_text[:100]}...")
        
        # === RETURN RESPONSE ===
        return ChatResponse(
            chat_id=chat_id,
            message=ai_response,
            context_used=context_used,
            was_summarized=was_summarized,
            history_used=len(recent_messages),
            has_summary=summary is not None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in send_message: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/history/{chat_id}", status_code=status.HTTP_200_OK)
async def get_chat_history(chat_id: str, limit: int = 50):
    """
    Lấy lịch sử chat
    
    Args:
        chat_id: ID của chat
        limit: Số lượng messages tối đa (mặc định 50)
    """
    try:
        chat = await chat_service.get_chat(chat_id)
        
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        # Lấy messages (giới hạn số lượng)
        messages = chat.get("messages", [])[-limit:]
        
        return {
            "chat_id": chat_id,
            "title": chat.get("title", "New Chat"),
            "summary": chat.get("summary"),
            "messages": messages,
            "total_messages": len(chat.get("messages", [])),
            "created_at": chat.get("created_at"),
            "updated_at": chat.get("updated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/list/{user_id}", status_code=status.HTTP_200_OK)
async def list_user_chats(user_id: str, limit: int = 50):
    """
    Lấy danh sách chats của user
    
    Args:
        user_id: ID của user
        limit: Số lượng chats tối đa
    """
    try:
        chats = await chat_service.list_user_chats(user_id=user_id, limit=limit)
        
        return {
            "user_id": user_id,
            "total_chats": len(chats),
            "chats": chats
        }
        
    except Exception as e:
        print(f"Error listing chats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{chat_id}", status_code=status.HTTP_200_OK)
async def delete_chat(chat_id: str):
    """
    Xóa một chat (soft delete)
    
    Args:
        chat_id: ID của chat
    """
    try:
        success = await chat_service.delete_chat(chat_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found or already deleted"
            )
        
        return {
            "message": "Chat deleted successfully",
            "chat_id": chat_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/regenerate-summary/{chat_id}", status_code=status.HTTP_200_OK)
async def regenerate_summary(chat_id: str):
    """
    Tạo lại tóm tắt cho một chat
    
    Args:
        chat_id: ID của chat
    """
    try:
        # Lấy toàn bộ messages
        chat = await chat_service.get_chat(chat_id)
        
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        messages = chat.get("messages", [])
        
        if len(messages) < 5:
            return {
                "message": "Not enough messages to generate summary",
                "chat_id": chat_id
            }
        
        # Generate summary
        print(f"Regenerating summary for chat {chat_id}...")
        summary_text = rag_service.llm.generate_summary(messages)
        
        # Lưu summary
        await chat_service.update_summary(chat_id, summary_text)
        
        return {
            "message": "Summary regenerated successfully",
            "chat_id": chat_id,
            "summary": summary_text
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error regenerating summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

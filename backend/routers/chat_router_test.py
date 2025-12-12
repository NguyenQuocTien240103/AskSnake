import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends, Query
from typing import Annotated  
from services.UserService import UserService
from services.RagService import RagService # mở đoạn này ra
from services.ImageService import ImageService # mở đoạn này ra
from config.rag_config import RagConfig # mở đoạn này ra
from services.ChatHistoryService import ChatHistoryService
from pydantics.chat import ChatRequest, ChatResponse
from PIL import Image
from io import BytesIO
import uuid
from datetime import datetime

app_router = APIRouter()

rag_service = RagService() # mở đoạn này ra
image_service = ImageService() # mở đoạn này ra


# Load existing RAG index
if not rag_service.load_existing_index(): # mở đoạn này ra
    print("Warning: No existing RAG index found.") # mở đoạn này ra

# Cấu hình
MAX_MESSAGES_BEFORE_SUMMARY = 4  # Tự động tóm tắt sau 4 messages (2 turns: user + AI)
RECENT_MESSAGES_COUNT = 3  # Lấy 3 messages gần nhất (giảm để tiết kiệm context)

@app_router.post("/prompt",response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def get_answer(current_user: Annotated[dict, Depends(UserService.get_current_user)], chat_id: str = Form(None), message: str = Form(None), file: UploadFile = File(None)):
    user_id = current_user['_id']
    print(f"Received prompt request from user {user_id} with chat_id={chat_id}, message={message}, file={file}")
    # result = None
    # if chat_id is None:
    #     result = await ChatHistoryService.create_new_chat_history(user_id,title=message)
    # return {"message": message, "result": str(result)}
    
    try:
        # === VALIDATION: Phải có ít nhất message HOẶC file ===
        unique_filename = "" 
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
            print(f"Detected snake: {snake_name} (confidence: {detection_result['probability']:.2%})")

             # Đường dẫn thư mục nơi lưu ảnh
            upload_folder = "static"
            
            # Kiểm tra xem thư mục đã tồn tại chưa
            if not os.path.exists(upload_folder):
                print(f"📂 Creating folder {upload_folder}...")
                os.makedirs(upload_folder)  # Tạo thư mục nếu chưa có

            # # Xác định đường dẫn lưu file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}_{file.filename}"
            file_path = os.path.join(upload_folder, unique_filename)

            image = Image.open(BytesIO(file_bytes))
            image = image.convert("RGB")
            image.save(file_path)

            # # Lưu file vào thư mục
            # with open(file_path, "wb") as f:
            #     f.write(file_bytes)

            # Nếu chỉ có ảnh không có text -> set default message
            if not message:
                user_message_content = f"[Uploaded image of {snake_name}]"
                print(f"Image-only mode: Auto-generated message for storage")
        
        # === STEP 2: Tạo chat mới nếu chưa có ===
        if not chat_id:
            # title = f"Chat về {snake_name}" if snake_name else "New Chat"
            title = message
            chat_id = await ChatHistoryService.create_new_chat_history(user_id=user_id, title=title)
            print(f"Created new chat: {chat_id}")
        else:
            # Verify chat exists
            existing_chat = await ChatHistoryService.get_chat_history(chat_id)
            if not existing_chat:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat not found"
                )
        
        # === STEP 3: Lưu message của user vào MongoDB (role=human) ===
        print(f"Saving user message to MongoDB...")
        success = await ChatHistoryService.add_message(
            chat_id=chat_id,
            role="human",
            content=user_message_content,
            file_name=unique_filename,
            metadata=metadata
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save user message"
            )
        
        # === STEP 4: Lấy 10 messages gần nhất + summary từ MongoDB ===
        print(f"Fetching recent chat history...")
        recent_messages = await ChatHistoryService.get_recent_messages(
            chat_id=chat_id, 
            limit=RECENT_MESSAGES_COUNT
        )
        
        summary = await ChatHistoryService.get_chat_summary(chat_id)
        
        print(f"Retrieved {len(recent_messages)} recent messages")
        if summary:
            print(f"Found existing summary: {summary[:100]}...")
        
        # Log chi tiết history để debug
        print(f"\nDEBUG - Chat History Being Used:")
        for i, msg in enumerate(recent_messages, 1):
            role_emoji = "👤" if msg["role"] == "human" else "🤖"
            print(f"  {i}. {role_emoji} [{msg['role']}]: {msg['content'][:80]}...")
        
        # === STEP 5: Query RAG để lấy context từ Qdrant ===
        print(f"Querying RAG for relevant context...")
        
        # Case 1: Có ảnh (với hoặc không có câu hỏi)
        if snake_name:
            print(f"Image detected: {snake_name}")
            if message:
                print(f"User question: {message}")
            else:
                print(f"No specific question - will provide general description")
            
            rag_result = rag_service.query_with_image(
                snake_name=snake_name,
                user_question=message,  # None if image-only
                top_k=RagConfig.TOP_K_RESULTS,
                chat_history=recent_messages,
                summary=summary
            )
        # Case 2: Chỉ có text (không có ảnh)
        else:
            print(f"Text-only query: {message}")
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
        
        print(f"RAG response generated (used {context_used} context chunks)")
        
        # === STEP 6: Lưu response của AI vào MongoDB (role=ai) ===
        print(f"Saving AI response to MongoDB...")
        ai_metadata = {
            "context_chunks_used": context_used,
            "reranking_used": rag_result.get("rerank_info", {}).get("reranking_used", False)
        }
        
        success = await ChatHistoryService.add_message(
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
        total_messages = await ChatHistoryService.get_message_count(chat_id)
        
        print(f"Total messages in chat: {total_messages}")
        
        if total_messages >= MAX_MESSAGES_BEFORE_SUMMARY and not summary:
            print(f"Chat has {total_messages} messages, generating summary...")
            
            # Lấy toàn bộ messages để tóm tắt
            all_messages = await ChatHistoryService.get_recent_messages(
                chat_id=chat_id,
                limit=total_messages
            )
            
            # Generate summary bằng LLM
            summary_text = rag_service.llm.generate_summary(all_messages)
            
            # Lưu summary vào MongoDB
            await ChatHistoryService.update_summary(chat_id, summary_text)
            was_summarized = True
            print(f"Summary generated and saved: {summary_text[:100]}...")
        
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
        print(f"Error in send_message: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )





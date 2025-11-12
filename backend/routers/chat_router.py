from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from services.ImageService import ImageService
from services.RagService import RagService

app_router = APIRouter()
image_service = ImageService()
rag_service = RagService()

# Kiểm tra xem có index sẵn chưa
if not rag_service.load_existing_index():
    print("No existing index found. Please run with --ingest first.")

@app_router.post("/prompt", status_code=status.HTTP_200_OK)
async def get_answer(
    message: str = Form(None),
    file: UploadFile = File(None)
):
    try:
        # Trường hợp 1: Chỉ có file (upload ảnh rắn) -> Mô tả tổng quan
        if file and not message:
            file_bytes = await file.read()
            result = await image_service.detect_image(file_bytes)
            snake_name = result["predicted_class"]
            
            # Query RAG với prompt mô tả (được tạo trong RagService)
            result_rag = rag_service.query_with_image(snake_name=snake_name)
            
            if "error" in result_rag:
                return {
                    "message": "Image processed successfully but RAG query failed",
                    "prediction": snake_name,
                    "probability": result["probability"],
                    "description": "Không tìm thấy thông tin chi tiết về loài rắn này."
                }
            
            return {
                "message": "Image and RAG processed successfully",
                "prediction": snake_name,
                "probability": result["probability"],
                "description": result_rag["response"],
                "context_used": result_rag.get("num_context_chunks", 0)
            }

        # Trường hợp 2: Chỉ có message (không có ảnh) -> Query thông thường
        elif message and not file:
            result_rag = rag_service.query(message)
            if "error" in result_rag:
                return {
                    "message": "RAG query failed",
                    "received_message": message,
                    "response_rag": result_rag["error"]
                }
            return {
                "message": "RAG query successful",
                "received_message": message,
                "response_rag": result_rag["response"]
            }

        # Trường hợp 3: Có cả file và message -> Trả lời câu hỏi cụ thể về con rắn
        elif file and message:
            file_bytes = await file.read()
            result = await image_service.detect_image(file_bytes)
            snake_name = result["predicted_class"]
            
            # Query RAG với prompt câu hỏi (được tạo trong RagService)
            result_rag = rag_service.query_with_image(
                snake_name=snake_name, 
                user_question=message
            )

            if "error" in result_rag:
                return {
                    "message": "Image processed but RAG query failed",
                    "received_message": message,
                    "prediction": snake_name,
                    "probability": result["probability"],
                    "response_rag": result_rag.get("error", "Không tìm thấy thông tin")
                }

            return {
                "message": "Image and RAG processed successfully",
                "received_message": message,
                "prediction": snake_name,
                "probability": result["probability"],
                "description": result_rag["response"],  # Đổi từ response_rag → description
                "context_used": result_rag.get("num_context_chunks", 0)
            }

        # Trường hợp không có gì
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You must provide either a file or a message."
            )

    except Exception as e:
        print("Error:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )





# from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
# from services.ImageService import ImageService
# from services.RagService import RagService
# import os

# app_router = APIRouter()
# image_service = ImageService()
# rag_service = RagService()

# # Kiểm tra xem có index sẵn chưa
# if not rag_service.load_existing_index():
#     print("No existing index found. Please run with --ingest first.")


# @app_router.post("/prompt", status_code=status.HTTP_200_OK)
# async def get_answer(
#     message: str = Form(...),
#     file: UploadFile = File(None)
# ):
#     try:
#         # Nếu không có file, chỉ trả về message
#         if not file:
#             return {
#                 "message": "No file uploaded",
#                 "received_message": message
#             }

#         # Đọc file bytes
#         file_bytes = await file.read()

#         # Gọi hàm detect
#         result = await image_service.detect_image(file_bytes)

#         # Nếu không có message thì chỉ trả kết quả ảnh
#         if not message:
#             return {
#                 "message": "Image processed successfully",
#                 "received_message": message,
#                 "prediction": result["predicted_class"],
#                 "probability": result["probability"]
#             }

#         # Nếu có message, gọi RAG
#         result_rag = rag_service.query(message)

#         if "error" in result_rag:
#             return {
#                 "message": "Image processed successfully",
#                 "received_message": message,
#                 "response_rag": result_rag["error"],
#                 "prediction": result["predicted_class"],
#                 "probability": result["probability"]
#             }

#         # Trả về kết quả cả ảnh và RAG
#         return {
#             "message": "Image processed successfully",
#             "received_message": message,
#             "response_rag": result_rag["response"],
#             "prediction": result["predicted_class"],
#             "probability": result["probability"]
#         }

#     except Exception as e:
#         print("Error:", e)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         )

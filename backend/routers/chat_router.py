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
        # Trường hợp: chỉ có file
        if file and not message:
            file_bytes = await file.read()
            result = await image_service.detect_image(file_bytes)
            return {
                "message": "Image processed successfully",
                "prediction": result["predicted_class"],
                "probability": result["probability"]
            }

        # Trường hợp: chỉ có message
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

        # Trường hợp: có cả file và message
        elif file and message:
            file_bytes = await file.read()
            result = await image_service.detect_image(file_bytes)
            result_rag = rag_service.query(message)

            if "error" in result_rag:
                return {
                    "message": "Image and RAG processed with partial success",
                    "received_message": message,
                    "response_rag": result_rag["error"],
                    "prediction": result["predicted_class"],
                    "probability": result["probability"]
                }

            return {
                "message": "Image and RAG processed successfully",
                "received_message": message,
                "response_rag": result_rag["response"],
                "prediction": result["predicted_class"],
                "probability": result["probability"]
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

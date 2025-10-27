from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from services.ImageService import ImageService
import os
app_router = APIRouter()
image_service = ImageService()

@app_router.post("/prompt", status_code=status.HTTP_200_OK)
async def get_answer(
    message: str = Form(...),
    file: UploadFile = File(None)
):
    try:
        if not file:
            return {"message": "No file uploaded", "received_message": message}

        # Đọc file bytes
        file_bytes = await file.read()
        # Gọi hàm detect
        result = await image_service.detect_image(file_bytes)

        return {
            "message": "Image processed successfully",
            "received_message": message,
            "prediction": result["predicted_class"],
            "probability": result["probability"]
        }

    except Exception as e:
        print("Error:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

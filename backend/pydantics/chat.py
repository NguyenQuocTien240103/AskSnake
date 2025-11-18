from pydantic import BaseModel, Field, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from typing import List, Optional, Literal, Any
from datetime import datetime
from bson import ObjectId

class Message(BaseModel):
    """Model cho một message trong conversation"""
    role: Literal["human", "ai", "system"] = Field(..., description="Vai trò của message")
    content: str = Field(..., description="Nội dung message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Thời gian tạo message")
    metadata: Optional[dict] = Field(default=None, description="Metadata bổ sung (snake_name, probability, etc.)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "role": "human",
                "content": "Rắn hổ mang có độc không?",
                "timestamp": "2024-01-01T00:00:00",
                "metadata": None
            }
        }
    }


class ChatRequest(BaseModel):
    """Request body cho chat API"""
    chat_id: Optional[str] = Field(default=None, description="ID của chat (None để tạo mới)")
    user_id: str = Field(..., description="ID của user")
    message: str = Field(..., description="Tin nhắn từ user")
    snake_name: Optional[str] = Field(default=None, description="Tên rắn nếu có upload ảnh")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "chat_id": "507f1f77bcf86cd799439011",
                "user_id": "user123",
                "message": "Rắn hổ mang có độc không?",
                "snake_name": None
            }
        }
    }


class ChatResponse(BaseModel):
    """Response body cho chat API"""
    chat_id: str = Field(..., description="ID của chat")
    message: str = Field(..., description="Message từ AI")
    context_used: int = Field(default=0, description="Số context chunks được sử dụng")
    was_summarized: bool = Field(default=False, description="Hội thoại có được tóm tắt không")
    history_used: int = Field(default=0, description="Số messages trong history được sử dụng")
    has_summary: bool = Field(default=False, description="Chat có summary không")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "chat_id": "507f1f77bcf86cd799439011",
                "message": "Có, rắn hổ mang là loài rắn độc...",
                "context_used": 5,
                "was_summarized": False,
                "history_used": 4,
                "has_summary": False
            }
        }
    }

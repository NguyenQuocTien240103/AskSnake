from pydantic import BaseModel, Field, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from typing import List, Optional, Literal, Any
from datetime import datetime
from bson import ObjectId

class PyObjectId(str):
    """Custom type for MongoDB ObjectId that works with Pydantic v2"""
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Any,
    ) -> core_schema.CoreSchema:
        """Pydantic v2 validation schema"""
        def validate_object_id(value: Any) -> str:
            if isinstance(value, ObjectId):
                return str(value)
            if isinstance(value, str):
                if ObjectId.is_valid(value):
                    return value
                raise ValueError("Invalid ObjectId")
            raise ValueError("Invalid ObjectId type")
        
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate_object_id),
            ])
        ], serialization=core_schema.plain_serializer_function_ser_schema(
            lambda x: str(x)
        ))
    
    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """JSON schema for OpenAPI docs"""
        return {"type": "string"}


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


class Chat(BaseModel):
    """Model cho một cuộc hội thoại"""
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str = Field(..., description="ID của user sở hữu chat này")
    title: Optional[str] = Field(default="New Chat", description="Tiêu đề của cuộc hội thoại")
    messages: List[Message] = Field(default_factory=list, description="Danh sách các messages")
    summary: Optional[str] = Field(default=None, description="Tóm tắt cuộc hội thoại (khi quá dài)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Thời gian tạo")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Thời gian cập nhật gần nhất")
    is_active: bool = Field(default=True, description="Chat có đang active không")

    model_config = {
        "arbitrary_types_allowed": True,
        "populate_by_name": True,
        "json_encoders": {ObjectId: str},
        "json_schema_extra": {
            "example": {
                "user_id": "user123",
                "title": "Hỏi về rắn hổ mang",
                "messages": [],
                "summary": None,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "is_active": True
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

"""
ChatService - Quản lý lịch sử chat và tương tác với MongoDB
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from config.database import db
from pydantics.chat import Chat, Message, ChatRequest

# MongoDB collections
chats_collection = db.get_collection("chats")

class ChatService:
    """Service để quản lý chat history trong MongoDB"""
    
    @staticmethod
    async def create_chat(user_id: str, title: str = "New Chat") -> str:
        """
        Tạo một cuộc hội thoại mới
        
        Args:
            user_id: ID của user
            title: Tiêu đề chat
            
        Returns:
            chat_id: ID của chat vừa tạo
        """
        chat_data = {
            "user_id": user_id,
            "title": title,
            "messages": [],
            "summary": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        
        result = await chats_collection.insert_one(chat_data)
        return str(result.inserted_id)
    
    @staticmethod
    async def get_chat(chat_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin một cuộc hội thoại
        
        Args:
            chat_id: ID của chat
            
        Returns:
            Chat document hoặc None
        """
        try:
            chat = await chats_collection.find_one({"_id": ObjectId(chat_id)})
            if chat:
                chat["_id"] = str(chat["_id"])
            return chat
        except Exception as e:
            print(f"Error getting chat: {e}")
            return None
    
    @staticmethod
    async def add_message(
        chat_id: str, 
        role: str, 
        content: str, 
        metadata: Optional[dict] = None
    ) -> bool:
        """
        Thêm message vào chat
        
        Args:
            chat_id: ID của chat
            role: "human", "ai", hoặc "system"
            content: Nội dung message
            metadata: Metadata bổ sung
            
        Returns:
            True nếu thành công
        """
        try:
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow(),
                "metadata": metadata or {}
            }
            
            result = await chats_collection.update_one(
                {"_id": ObjectId(chat_id)},
                {
                    "$push": {"messages": message},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error adding message: {e}")
            return False
    
    @staticmethod
    async def get_recent_messages(chat_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Lấy N messages gần nhất từ chat
        
        Args:
            chat_id: ID của chat
            limit: Số lượng messages cần lấy
            
        Returns:
            List của messages
        """
        try:
            chat = await chats_collection.find_one(
                {"_id": ObjectId(chat_id)},
                {"messages": {"$slice": -limit}}
            )
            
            if chat and "messages" in chat:
                return chat["messages"]
            return []
        except Exception as e:
            print(f"Error getting recent messages: {e}")
            return []
    
    @staticmethod
    async def update_summary(chat_id: str, summary: str) -> bool:
        """
        Cập nhật tóm tắt cho chat
        
        Args:
            chat_id: ID của chat
            summary: Nội dung tóm tắt
            
        Returns:
            True nếu thành công
        """
        try:
            result = await chats_collection.update_one(
                {"_id": ObjectId(chat_id)},
                {
                    "$set": {
                        "summary": summary,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating summary: {e}")
            return False
    
    @staticmethod
    async def get_chat_summary(chat_id: str) -> Optional[str]:
        """
        Lấy tóm tắt của chat
        
        Args:
            chat_id: ID của chat
            
        Returns:
            Summary string hoặc None
        """
        try:
            chat = await chats_collection.find_one(
                {"_id": ObjectId(chat_id)},
                {"summary": 1}
            )
            return chat.get("summary") if chat else None
        except Exception as e:
            print(f"Error getting summary: {e}")
            return None
    
    @staticmethod
    async def get_message_count(chat_id: str) -> int:
        """
        Đếm số lượng messages trong chat
        
        Args:
            chat_id: ID của chat
            
        Returns:
            Số lượng messages
        """
        try:
            chat = await chats_collection.find_one(
                {"_id": ObjectId(chat_id)},
                {"messages": 1}
            )
            return len(chat.get("messages", [])) if chat else 0
        except Exception as e:
            print(f"Error counting messages: {e}")
            return 0
    
    @staticmethod
    async def list_user_chats(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Lấy danh sách chats của user
        
        Args:
            user_id: ID của user
            limit: Số lượng chats tối đa
            
        Returns:
            List của chat documents
        """
        try:
            cursor = chats_collection.find(
                {"user_id": user_id, "is_active": True}
            ).sort("updated_at", -1).limit(limit)
            
            chats = []
            async for chat in cursor:
                chat["_id"] = str(chat["_id"])
                # Chỉ lấy thông tin cơ bản, không lấy toàn bộ messages
                chats.append({
                    "_id": chat["_id"],
                    "title": chat.get("title", "New Chat"),
                    "created_at": chat.get("created_at"),
                    "updated_at": chat.get("updated_at"),
                    "message_count": len(chat.get("messages", []))
                })
            
            return chats
        except Exception as e:
            print(f"Error listing chats: {e}")
            return []
    
    @staticmethod
    async def delete_chat(chat_id: str) -> bool:
        """
        Xóa mềm một chat (set is_active = False)
        
        Args:
            chat_id: ID của chat
            
        Returns:
            True nếu thành công
        """
        try:
            result = await chats_collection.update_one(
                {"_id": ObjectId(chat_id)},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error deleting chat: {e}")
            return False
    
    @staticmethod
    def messages_to_dict_format(messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Convert MongoDB messages to simple dict format for LLM
        
        Args:
            messages: List của message dicts từ MongoDB
            
        Returns:
            List của simplified message dicts
        """
        simplified_messages = []
        
        for msg in messages:
            simplified_messages.append({
                "role": msg.get("role", "human"),
                "content": msg.get("content", "")
            })
        
        return simplified_messages

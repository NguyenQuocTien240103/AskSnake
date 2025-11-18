from fastapi import HTTPException, status, Depends
from config.database import db
from typing import List, Optional, Dict, Any, Annotated
from datetime import datetime
from bson import ObjectId


class ChatHistoryService:
    async def create_new_chat_history(user_id: str, title: str = "New Chat") -> str:
        chat_history_data = {
            "user_id": user_id,
            "title": title,
            "messages": [],
            "summary": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await db["chat_history"].insert_one(chat_history_data)
        return str(result.inserted_id)
    async def get_chat_history(chat_id: str) -> Optional[Dict[str, Any]]:
        try:
            chat = await db["chat_history"].find_one({"_id": ObjectId(chat_id)})
            if chat:
                chat["_id"] = str(chat["_id"])
            return chat
        except Exception as e:
            print(f"Error getting chat: {e}")
            return None
    async def add_message(chat_id: str,  role: str,  content: str,  metadata: Optional[dict] = None) -> bool:
        try:
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow(),
                "metadata": metadata or {}
            }
            
            result = await db["chat_history"].update_one(
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
    async def get_chat_summary(chat_id: str) -> Optional[str]:
        try:
            chat = await db["chat_history"].find_one(
                {"_id": ObjectId(chat_id)},
                {"summary": 1}
            )
            return chat.get("summary") if chat else None
        except Exception as e:
            print(f"Error getting summary: {e}")
            return None
    async def get_message_count(chat_id: str) -> int:
        try:
            chat = await db["chat_history"].find_one(
                {"_id": ObjectId(chat_id)},
                {"messages": 1}
            )
            return len(chat.get("messages", [])) if chat else 0
        except Exception as e:
            print(f"Error counting messages: {e}")
            return 0
    async def get_recent_messages(chat_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            chat = await db["chat_history"].find_one(
                {"_id": ObjectId(chat_id)},
                {"messages": {"$slice": -limit}}
            )
            
            if chat and "messages" in chat:
                return chat["messages"]
            return []
        except Exception as e:
            print(f"Error getting recent messages: {e}")
            return []
    async def update_summary(chat_id: str, summary: str) -> bool:
        try:
            result = await db["chat_history"].update_one(
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
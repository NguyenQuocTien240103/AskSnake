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
    async def add_message(chat_id: str,  role: str,  content: str, file_name: Optional[str] = None, metadata: Optional[dict] = None) -> bool:
        try:
            print("file_name=",file_name)

            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow(),
                "file_name": file_name,
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
        
    #----------------------------Lịch sử với k có session user------------------------------ #
    async def create_new_chat_public_history(title: str = "New Chat") -> str:
        chat_history_data = {
            # "user_id": user_id,
            "title": title,
            "messages": [],
            "summary": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await db["chat_history_public"].insert_one(chat_history_data)
        return str(result.inserted_id)
    async def get_chat_public_history(chat_id: str) -> Optional[Dict[str, Any]]:
        try:
            chat = await db["chat_history_public"].find_one({"_id": ObjectId(chat_id)})
            if chat:
                chat["_id"] = str(chat["_id"])
            return chat
        except Exception as e:
            print(f"Error getting chat: {e}")
            return None
    async def add_message_public(chat_id: str,  role: str,  content: str, file_name: Optional[str] = None, metadata: Optional[dict] = None) -> bool:
        try:
            print("file_name=",file_name)

            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow(),
                "file_name": file_name,
                "metadata": metadata or {}
            }
            
            result = await db["chat_history_public"].update_one(
                {"_id": ObjectId(chat_id)},
                {
                    "$push": {"messages": message},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error adding message: {e}")
        except Exception as e:
            print(f"Error adding message: {e}")
            return False
    async def get_chat_public_summary(chat_id: str) -> Optional[str]:
        try:
            chat = await db["chat_history_public"].find_one(
                {"_id": ObjectId(chat_id)},
                {"summary": 1}
            )
            return chat.get("summary") if chat else None
        except Exception as e:
            print(f"Error getting summary: {e}")
            return None
    async def get_message_count_public(chat_id: str) -> int:
        try:
            chat = await db["chat_history_public"].find_one(
                {"_id": ObjectId(chat_id)},
                {"messages": 1}
            )
            return len(chat.get("messages", [])) if chat else 0
        except Exception as e:
            print(f"Error counting messages: {e}")
            return 0
    async def get_recent_messages_public(chat_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            chat = await db["chat_history_public"].find_one(
                {"_id": ObjectId(chat_id)},
                {"messages": {"$slice": -limit}}
            )
            
            if chat and "messages" in chat:
                return chat["messages"]
            return []
        except Exception as e:
            print(f"Error getting recent messages: {e}")
            return []
    async def update_summary_public(chat_id: str, summary: str) -> bool:
        try:
            result = await db["chat_history_public"].update_one(
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
    
    # ---------------------------------------------------------------- #
    async def delete_chat_history(user_id: str, chat_id: str) -> bool:
        try:
            result = await db["chat_history"].delete_one({
                "_id": ObjectId(chat_id),
                "user_id": user_id
            })
            return result.deleted_count == 1
        except Exception as e:
            print(f"Error deleting chat: {e}")
            return False
    async def rename_chat_history(user_id: str, chat_id: str, new_name: str) -> bool:
        try:
            result = await db["chat_history"].update_one(
                {
                    "_id": ObjectId(chat_id),
                    "user_id": user_id
                },
                {
                    "$set": {"title": new_name}  # hoặc field tương ứng với tên chat
                }
            )
            return result.modified_count == 1
        except Exception as e:
            print(f"Error renaming chat: {e}")
            return False
    # ---------------------------Lịch sử ảnh dự đoán---------------------------------- #
    async def add_history_predict(label: str, confident: str, file_name: Optional[str] = None) -> bool:
        try:
            print("file_name=",file_name)

            document = {
                "confident": confident,
                "label": label,
                "file_name": file_name,
                "timestamp": datetime.utcnow(),
            }
            
            result = await db["history_predict"].insert_one(document)
            return result.inserted_id is not None
            
        except Exception as e:
            print(f"Error adding history predict: {e}")
            return False
        

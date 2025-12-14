from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, APIKeyCookie
from utils.AuthUtlis import AuthUtils
from pydantics.user import UserBase
from config.database import db
from dotenv import load_dotenv
from datetime import timedelta
from typing import Annotated, Counter
import os
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

load_dotenv()
api_key_cookie = APIKeyCookie(name="access_token", auto_error=False)

class HistoryPredictService:
    # async def get_all_history_predict(page: int =1, limit: int =10) -> dict:

        # col = db["users"]
        # skip = (page - 1) * limit
        # filter = {"role":"user"}
        # cursor = (
        #     col.find(filter)
        #     .sort("createdAt", -1)
        #     .skip(skip)
        #     .limit(limit)
        # )
        # data = await cursor.to_list(limit)
        # for item in data:
        #     item["_id"] = str(item["_id"])
        #     item.pop("password", None)
        # total = await col.count_documents(filter)
        # return {
        #     "page": page,
        #     "limit": limit,
        #     "total": total,
        #     "data": data
        # }
    async def get_all_history_predict() -> dict:
        cursor = db["history_predict"].find().sort("created_at", -1)
        result = []
        labels = []

        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            result.append(doc)

            if "label" in doc and doc["label"]:
                labels.append(doc["label"])

        label_count = dict(Counter(labels))

        return {
            "items": result,
            "label_count": label_count
        }
    
    async def get_detail_history_predict(label: str) -> dict:
        cursor = db["history_predict"].find({"label": label}).sort("created_at", -1)
        result = []

        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            result.append(doc)

        return {
            "items": result
        }
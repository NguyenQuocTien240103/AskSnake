from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, APIKeyCookie
from utils.AuthUtlis import AuthUtils
from pydantics.user import UserBase
from config.database import db
from dotenv import load_dotenv
from datetime import timedelta
from typing import Annotated
import os

load_dotenv()
api_key_cookie = APIKeyCookie(name="access_token", auto_error=False)

class UserService:
    async def get_current_user(access_token: Annotated[str, Depends(api_key_cookie)]) -> UserBase:
        print("access_token",access_token)
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        payload = AuthUtils.verify_token(access_token)
        email = payload.get("email")
        
        if email is None:
            raise credentials_exception

        user = await db["users"].find_one({"email": email})

        if user is None:
            raise credentials_exception
            
        return UserBase(email=user['email'])
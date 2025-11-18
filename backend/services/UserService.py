from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, APIKeyCookie
from utils.AuthUtlis import AuthUtils
from pydantics.user import UserBase
from config.database import db
from dotenv import load_dotenv
from datetime import timedelta
from typing import Annotated
import os
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

load_dotenv()
api_key_cookie = APIKeyCookie(name="access_token", auto_error=False)

class UserService:
    async def get_current_user(access_token: Annotated[str, Depends(api_key_cookie)]) -> dict:
        # print("access_token",access_token)
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = AuthUtils.verify_token(access_token)
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token has expired. Please refresh your token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except (InvalidTokenError, Exception):
            raise credentials_exception
            
        email = payload.get("email")
        
        if email is None:
            raise credentials_exception

        user = await db["users"].find_one({"email": email})

        if user is None:
            raise credentials_exception
            
        # return UserBase(email=user['email'])
        return user
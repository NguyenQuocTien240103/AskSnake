from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from utils.AuthUtlis import AuthUtils
from pydantics.user import UserBase
from pydantics.token import Token
from config.database import db
from dotenv import load_dotenv
from datetime import timedelta
from typing import Annotated
import os

load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserService:
    async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserBase:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        payload = AuthUtils.verify_token(token)
        email = payload.get("email")
        
        if email is None:
            raise credentials_exception

        user = await db["users"].find_one({"email": email})

        if user is None:
            raise credentials_exception
            
        return UserBase(email=user['email'])
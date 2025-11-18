from fastapi.security import OAuth2PasswordBearer, APIKeyCookie
from fastapi import HTTPException, status, Depends
from datetime import timedelta,datetime
from utils.AuthUtlis import AuthUtils
from pydantics.token import Token, AccessToken
from config.database import db
from dotenv import load_dotenv
from typing import Annotated
import os
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

load_dotenv()
api_key_cookie = APIKeyCookie(name="refresh_token", auto_error=False)

class AuthService:
    async def get_token(email: str, password: str) -> Token:
        user = await db["users"].find_one({"email": email})

        if user is None or not AuthUtils.verify_password(password, user['password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email or Passowrd is not matching",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        access_token_expires = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECOND"))  
        access_token = AuthUtils.create_token(data={"email": user['email']}, expires_delta=access_token_expires)
        refresh_token_expires = int(os.getenv("REFRESH_TOKEN_EXPIRE_SECOND"))  
        refresh_token = AuthUtils.create_token(data={"email": user['email']}, expires_delta=refresh_token_expires)
        result = await db["refresh_token"].insert_one({"user_id": user["_id"], "token": refresh_token, "create_at": datetime.utcnow(), "expires_at": datetime.utcnow() + timedelta(days=7)})

        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = "Unable to complete login. Please try again later."
            )  

        return Token(access_token=access_token,refresh_token=refresh_token)
    async def get_access_token(refresh_token: Annotated[str, Depends(api_key_cookie)]) -> AccessToken:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is missing",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            payload = AuthUtils.verify_token(refresh_token)
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired. Please login again.",
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
    
        access_token_expires = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECOND"))  
        access_token = AuthUtils.create_token(data={"email": user['email']}, expires_delta=access_token_expires)
        return AccessToken(access_token=access_token)
    async def register_user(email: str, password: str):
        existing_user = await db["users"].find_one({"email": email})

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
            
        hashed_password = AuthUtils.hash_password(password)
        result = await db["users"].insert_one({"email": email, "password": hashed_password, "role": "user", "create_at": datetime.utcnow(), "update_at": datetime.utcnow()})
        return result.inserted_id
    async def verify_refresh_token(refresh_token: Annotated[str, Depends(api_key_cookie)]) -> str:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is missing",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            payload = AuthUtils.verify_token(refresh_token)
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired. Please login again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except (InvalidTokenError, Exception):
            raise credentials_exception
            
        email = payload.get("email")
        
        if email is None:
            raise credentials_exception

        result = await db["refresh_token"].delete_many({"token": refresh_token})

        if result.deleted_count == 0:
            raise credentials_exception
            
        return refresh_token
    async def update_password(current_user: dict, old_password: str, new_password: str):

        if not AuthUtils.verify_password(old_password, current_user['password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Update password is fail",
            )
        
        hashed_new_password = AuthUtils.hash_password(new_password)
        result = await db["users"].update_one(
            {"email": current_user['email']},
            {"$set": {"password": hashed_new_password}}
        )
        return result.modified_count
    
from fastapi import HTTPException, status
from utils.AuthUtlis import AuthUtils
from pydantics.token import Token
from dotenv import load_dotenv
from datetime import timedelta
from config.database import db
import os

load_dotenv()

class AuthService:
    async def get_access_token(email: str, password: str) -> Token:
        user = await db["users"].find_one({"email": email})

        if user is None or not AuthUtils.verify_password(password, user['password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email or Passowrd is not matching",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_SECOND")))     
        access_token = AuthUtils.create_access_token(data={"email": user['email']}, expires_delta=access_token_expires)
        return Token(access_token=access_token, token_type="bearer")
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
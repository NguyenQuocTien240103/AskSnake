from datetime import datetime, timedelta
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
import jwt
import bcrypt

load_dotenv()

class AuthUtils:
    def create_access_token(data: dict, expires_delta: int = 86400) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
        return encoded_jwt

    def verify_token(token: str) -> dict:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        return payload

    def hash_password(password: str) -> str:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)

    def verify_password(password: str, hashed_password: str) -> bool:
        return pwd_context.verify(password, hashed_password)
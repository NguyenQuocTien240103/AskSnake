from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from config.database import client, db
from routers.auth_router import app_router as auth_router
from routers.user_router import app_router as user_router
# from routers.chat_router import app_router as chat_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/user", tags=["user"])
# app.include_router(chat_router, prefix="/chat", tags=["chat"])


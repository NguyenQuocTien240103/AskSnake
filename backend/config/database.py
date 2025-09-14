from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

if not MONGO_URI or not DATABASE_NAME:
    raise ValueError("MONGO_URI or DATABASE_NAME is not set in the environment variables.")

try:
    client = AsyncIOMotorClient(MONGO_URI)
    client = AsyncIOMotorClient(MONGO_URI)
    db = client.get_database(DATABASE_NAME)
    print("MongoDB connection: Successfully")
except Exception as e:
    print("MongoDB connection: Failed", e)
    raise e

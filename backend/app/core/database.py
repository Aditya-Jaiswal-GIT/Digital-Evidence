from pymongo import MongoClient
from app.core.config import settings

client = MongoClient(
    settings.MONGO_URI,
    serverSelectionTimeoutMS=5000
)

database = client[settings.DATABASE_NAME]


def connect_database():
    client.admin.command("ping")
    print("MongoDB Atlas connected successfully!")


def close_database():
    client.close()
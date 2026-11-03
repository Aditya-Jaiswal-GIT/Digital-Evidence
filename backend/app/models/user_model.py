from datetime import datetime, timezone

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.core.database import database


users_collection = database["users"]


def create_user(user_data: dict):
    """
    Insert a new user into MongoDB.
    """

    user_data["created_at"] = datetime.now(timezone.utc)
    user_data["updated_at"] = datetime.now(timezone.utc)

    result = users_collection.insert_one(user_data)

    return str(result.inserted_id)


def get_user_by_email(email: str):
    """
    Find a user using email.
    """

    return users_collection.find_one({
        "email": email.lower()
    })


def get_user_by_id(user_id: str):
    """
    Find a user using MongoDB ObjectId.
    """

    if not ObjectId.is_valid(user_id):
        return None

    return users_collection.find_one({
        "_id": ObjectId(user_id)
    })


def email_exists(email: str) -> bool:
    """
    Check whether an email is already registered.
    """

    return users_collection.find_one({
        "email": email.lower()
    }) is not None
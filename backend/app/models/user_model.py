from datetime import datetime, timezone

from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument
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





def list_users(page: int = 1, page_size: int = 10):
    skip = (page - 1) * page_size

    cursor = (
        users_collection
        .find({}, {"password_hash": 0})
        .sort("created_at", -1)
        .skip(skip)
        .limit(page_size)
    )

    users = []

    for user in cursor:
        users.append({
            "id": str(user["_id"]),
            "full_name": user["full_name"],
            "email": user["email"],
            "role": user["role"],
            "is_active": user["is_active"],
            "is_verified": user["is_verified"],
            "created_at": user.get("created_at")
        })

    total = users_collection.count_documents({})

    return {
        "users": users,
        "total": total,
        "page": page,
        "page_size": page_size
    }


def update_user_profile(user_id: str, update_data: dict):
    if not ObjectId.is_valid(user_id):
        return None

    update_data["updated_at"] = datetime.now(timezone.utc)

    result = users_collection.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )

    if result is None:
        return None

    return {
        "id": str(result["_id"]),
        "full_name": result["full_name"],
        "email": result["email"],
        "role": result["role"],
        "is_active": result["is_active"],
        "is_verified": result["is_verified"]
    }


def update_user_role(user_id: str, role: str):
    if not ObjectId.is_valid(user_id):
        return None

    result = users_collection.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "role": role,
                "updated_at": datetime.now(timezone.utc)
            }
        },
      return_document=ReturnDocument.AFTER  
    )

    if result is None:
        return None

    return {
        "id": str(result["_id"]),
        "full_name": result["full_name"],
        "email": result["email"],
        "role": result["role"],
        "is_active": result["is_active"],
        "is_verified": result["is_verified"]
    }

def update_user_status(user_id: str, is_active: bool):
    if not ObjectId.is_valid(user_id):
        return None

    result = users_collection.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "is_active": is_active,
                "updated_at": datetime.now(timezone.utc)
            }
        },
        return_document=True
    )

    if result is None:
        return None

    return {
        "id": str(result["_id"]),
        "full_name": result["full_name"],
        "email": result["email"],
        "role": result["role"],
        "is_active": result["is_active"],
        "is_verified": result["is_verified"]
    }


def get_user_by_id_and_organization(
    user_id: str,
    organization_id: str
):
    if not ObjectId.is_valid(user_id):
        return None

    if not ObjectId.is_valid(organization_id):
        return None

    return users_collection.find_one({
        "_id": ObjectId(user_id),
        "organization_id": ObjectId(organization_id)
    })

def list_users_by_organization(
    organization_id: str,
    page: int = 1,
    page_size: int = 10
):
    if not ObjectId.is_valid(organization_id):
        return {
            "users": [],
            "total": 0,
            "page": page,
            "page_size": page_size
        }

    organization_object_id = ObjectId(organization_id)

    skip = (page - 1) * page_size

    cursor = (
        users_collection
        .find(
            {"organization_id": organization_object_id},
            {"password_hash": 0}
        )
        .sort("created_at", -1)
        .skip(skip)
        .limit(page_size)
    )

    users = []

    for user in cursor:
        users.append({
            "id": str(user["_id"]),
            "full_name": user["full_name"],
            "email": user["email"],
            "role": user["role"],
            "is_active": user["is_active"],
            "is_verified": user["is_verified"],
            "created_at": user.get("created_at")
        })

    total = users_collection.count_documents({
        "organization_id": organization_object_id
    })

    return {
        "users": users,
        "total": total,
        "page": page,
        "page_size": page_size
    }

def update_user_role_by_organization(
    user_id: str,
    organization_id: str,
    role: str
):
    if not ObjectId.is_valid(user_id):
        return None

    if not ObjectId.is_valid(organization_id):
        return None

    result = users_collection.find_one_and_update(
        {
            "_id": ObjectId(user_id),
            "organization_id": ObjectId(organization_id)
        },
        {
            "$set": {
                "role": role,
                "updated_at": datetime.now(timezone.utc)
            }
        },
        return_document=ReturnDocument.AFTER
    )

    if result is None:
        return None

    return {
        "id": str(result["_id"]),
        "full_name": result["full_name"],
        "email": result["email"],
        "role": result["role"],
        "is_active": result["is_active"],
        "is_verified": result["is_verified"]
    }

def update_user_status_by_organization(
    user_id: str,
    organization_id: str,
    is_active: bool
):
    if not ObjectId.is_valid(user_id):
        return None

    if not ObjectId.is_valid(organization_id):
        return None

    result = users_collection.find_one_and_update(
        {
            "_id": ObjectId(user_id),
            "organization_id": ObjectId(organization_id)
        },
        {
            "$set": {
                "is_active": is_active,
                "updated_at": datetime.now(timezone.utc)
            }
        },
        return_document=ReturnDocument.AFTER
    )

    if result is None:
        return None

    return {
        "id": str(result["_id"]),
        "full_name": result["full_name"],
        "email": result["email"],
        "role": result["role"],
        "is_active": result["is_active"],
        "is_verified": result["is_verified"]
    }

def assign_user_to_organization(
    user_id: str,
    organization_id: str
):
    if not ObjectId.is_valid(user_id):
        return None

    if not ObjectId.is_valid(organization_id):
        return None

    result = users_collection.find_one_and_update(
        {
            "_id": ObjectId(user_id),
            "organization_id": None
        },
        {
            "$set": {
                "organization_id": ObjectId(organization_id),
                "updated_at": datetime.now(timezone.utc)
            }
        },
        return_document=ReturnDocument.AFTER
    )

    if result is None:
        return None

    return {
        "id": str(result["_id"]),
        "full_name": result["full_name"],
        "email": result["email"],
        "role": result["role"],
        "organization_id": str(result["organization_id"]),
        "is_active": result["is_active"]
    }
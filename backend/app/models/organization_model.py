
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError

from app.core.database import database


organizations_collection = database["organizations"]


def create_organization(name: str, description: str = ""):
    organization = {
        "name": name.strip(),
        "description": description.strip(),
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }

    try:
        result = organizations_collection.insert_one(organization)
        return str(result.inserted_id)

    except DuplicateKeyError:
        raise ValueError("Organization already exists")


def get_organization_by_id(organization_id: str):
    from bson import ObjectId

    if not ObjectId.is_valid(organization_id):
        return None

    return organizations_collection.find_one({
        "_id": ObjectId(organization_id)
    })


def get_organization_by_name(name: str):
    return organizations_collection.find_one({
        "name": name.strip()
    })

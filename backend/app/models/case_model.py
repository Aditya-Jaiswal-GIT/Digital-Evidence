
from datetime import datetime, timezone

from bson import ObjectId
from pymongo import ReturnDocument

from app.core.database import database


cases_collection = database["cases"]


def create_case(case_data: dict):
    """Insert a new forensic case into MongoDB."""

    now = datetime.now(timezone.utc)

    case_data["created_at"] = now
    case_data["updated_at"] = now

    result = cases_collection.insert_one(case_data)

    return str(result.inserted_id)


def get_case_by_id(case_id: str, organization_id: str):
    """Retrieve a case within a specific organization."""

    if not ObjectId.is_valid(case_id):
        return None

    if not ObjectId.is_valid(organization_id):
        return None

    return cases_collection.find_one({
        "_id": ObjectId(case_id),
        "organization_id": ObjectId(organization_id)
    })


def get_case_by_number(case_number: str, organization_id: str):
    """Find a case using its case number within an organization."""

    if not ObjectId.is_valid(organization_id):
        return None

    return cases_collection.find_one({
        "case_number": case_number,
        "organization_id": ObjectId(organization_id)
    })


def list_cases(organization_id: str, page: int, page_size: int):
    """Return paginated cases belonging to an organization."""

    if not ObjectId.is_valid(organization_id):
        return [], 0

    skip = (page - 1) * page_size

    query = {
        "organization_id": ObjectId(organization_id)
    }

    cases = list(
        cases_collection.find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(page_size)
    )

    total = cases_collection.count_documents(query)

    return cases, total


def update_case(case_id: str, organization_id: str, update_data: dict):
    """Update a case within an organization."""

    if not ObjectId.is_valid(case_id):
        return None

    if not ObjectId.is_valid(organization_id):
        return None

    update_data["updated_at"] = datetime.now(timezone.utc)

    return cases_collection.find_one_and_update(
        {
            "_id": ObjectId(case_id),
            "organization_id": ObjectId(organization_id)
        },
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )


def delete_case(case_id: str, organization_id: str):
    """Delete a case within an organization."""

    if not ObjectId.is_valid(case_id):
        return False

    if not ObjectId.is_valid(organization_id):
        return False

    result = cases_collection.delete_one({
        "_id": ObjectId(case_id),
        "organization_id": ObjectId(organization_id)
    })

    return result.deleted_count == 1


def assign_investigator(case_id: str, organization_id: str, user_id: str):
    """Assign an investigator to a case."""

    if not all(ObjectId.is_valid(value) for value in
               [case_id, organization_id, user_id]):
        return None

    return cases_collection.find_one_and_update(
        {
            "_id": ObjectId(case_id),
            "organization_id": ObjectId(organization_id)
        },
        {
            "$addToSet": {
                "assigned_investigators": ObjectId(user_id)
            },
            "$set": {
                "updated_at": datetime.now(timezone.utc)
            }
        },
        return_document=ReturnDocument.AFTER
    )


def remove_investigator(case_id: str, organization_id: str, user_id: str):
    """Remove an investigator from a case."""

    if not all(ObjectId.is_valid(value) for value in
               [case_id, organization_id, user_id]):
        return None

    return cases_collection.find_one_and_update(
        {
            "_id": ObjectId(case_id),
            "organization_id": ObjectId(organization_id)
        },
        {
            "$pull": {
                "assigned_investigators": ObjectId(user_id)
            },
            "$set": {
                "updated_at": datetime.now(timezone.utc)
            }
        },
        return_document=ReturnDocument.AFTER
    )


def archive_case(case_id: str, organization_id: str, archived_by: str):
    """Soft-archive a closed case."""

    if not all(
        ObjectId.is_valid(value)
        for value in [case_id, organization_id, archived_by]
    ):
        return None

    return cases_collection.find_one_and_update(
        {
            "_id": ObjectId(case_id),
            "organization_id": ObjectId(organization_id),
            "status": "closed",
            "is_archived": {"$ne": True}
        },
        {
            "$set": {
                "is_archived": True,
                "archived_at": datetime.now(timezone.utc),
                "archived_by": ObjectId(archived_by),
                "updated_at": datetime.now(timezone.utc)
            }
        },
        return_document=ReturnDocument.AFTER
    )

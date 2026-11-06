
from datetime import datetime, timezone
from fastapi import HTTPException

from app.models import case_model
from app.models.audit_model import create_audit_log
from app.schemas.case_schema import CaseStatus
from bson import ObjectId
from app.models.user_model import get_user_by_id_and_organization

def get_organization_id(current_user: dict) -> str:
    """Get and validate the current user's organization ID."""

    organization_id = current_user.get("organization_id")

    if not organization_id:
        raise HTTPException(
            status_code=403,
            detail="Your account is not assigned to an organization"
        )

    organization_id = str(organization_id)

    from bson import ObjectId

    if not ObjectId.is_valid(organization_id):
        raise HTTPException(
            status_code=403,
            detail="Invalid organization assignment"
        )

    return organization_id


def generate_case_number(organization_id: str) -> str:
    """Generate a unique case number."""

    current_year = datetime.now(timezone.utc).year
    prefix = f"CASE-{current_year}"

    last_case = case_model.cases_collection.find_one(
        {
            "organization_id": __import__("bson").ObjectId(organization_id),
            "case_number": {"$regex": f"^{prefix}-"}
        },
        sort=[("case_number", -1)]
    )

    if last_case:
        last_number = int(last_case["case_number"].split("-")[-1])
        next_number = last_number + 1
    else:
        next_number = 1

    return f"{prefix}-{next_number:04d}"


def create_new_case(case_data: dict, current_user: dict):
    """Create a new forensic case."""

    organization_id = get_organization_id(current_user)

    case_number = generate_case_number(organization_id)

    case_document = {
        "case_number": case_number,
        "title": case_data["title"],
        "description": case_data["description"],
        "case_type": case_data["case_type"],
        "priority": case_data["priority"].value,
        "status": CaseStatus.OPEN.value,
        "organization_id": __import__("bson").ObjectId(organization_id),
        "created_by": current_user["_id"],
        "assigned_investigators": [],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }

    case_id = case_model.create_case(case_document)

    create_audit_log(
        actor_user_id=str(current_user["_id"]),
        action="case.created",
        target_user_id=None,
        organization_id=organization_id,
        changes={
            "case_id": case_id,
            "case_number": case_number,
            "title": case_data["title"]
        }
    )

    return case_model.get_case_by_id(case_id, organization_id)



def get_all_cases(current_user: dict, page: int = 1, page_size: int = 10):
    """Get paginated cases for the current user's organization."""

    organization_id = get_organization_id(current_user)

    if page < 1 or page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=400,
            detail="Invalid pagination parameters"
        )

    cases, total = case_model.list_cases(
        organization_id=organization_id,
        page=page,
        page_size=page_size
    )

    return {
        "cases": cases,
        "total": total,
        "page": page,
        "page_size": page_size
    }


def get_single_case(case_id: str, current_user: dict):
    """Get one case belonging to the current user's organization."""

    organization_id = get_organization_id(current_user)

    case = case_model.get_case_by_id(
        case_id=case_id,
        organization_id=organization_id
    )

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found"
        )

    return case


def update_case_details(
    case_id: str,
    update_data: dict,
    current_user: dict
):
    """Update case details within the user's organization."""

    organization_id = get_organization_id(current_user)

    # Remove fields that should never be changed here
    allowed_fields = {
        "title",
        "description",
        "case_type",
        "priority"
    }

    update_data = {
        key: value
        for key, value in update_data.items()
        if key in allowed_fields and value is not None
    }

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No valid fields provided for update"
        )

    updated_case = case_model.update_case(
        case_id=case_id,
        organization_id=organization_id,
        update_data=update_data
    )

    if not updated_case:
        raise HTTPException(
            status_code=404,
            detail="Case not found"
        )

    create_audit_log(
        actor_user_id=str(current_user["_id"]),
        action="case.updated",
        target_user_id=None,
        organization_id=organization_id,
        changes={
            "case_id": str(updated_case["_id"]),
            "updated_fields": list(update_data.keys())
        }
    )

    return updated_case


def update_case_status(
    case_id: str,
    new_status: CaseStatus,
    current_user: dict
):
    """Change the status of a case."""

    organization_id = get_organization_id(current_user)

    existing_case = case_model.get_case_by_id(
        case_id=case_id,
        organization_id=organization_id
    )

    if not existing_case:
        raise HTTPException(
            status_code=404,
            detail="Case not found"
        )

    if existing_case["status"] == CaseStatus.CLOSED.value:
        raise HTTPException(
            status_code=400,
            detail="Closed cases cannot be modified"
        )

    updated_case = case_model.update_case(
        case_id=case_id,
        organization_id=organization_id,
        update_data={"status": new_status.value}
    )

    create_audit_log(
        actor_user_id=str(current_user["_id"]),
        action="case.status_changed",
        target_user_id=None,
        organization_id=organization_id,
        changes={
            "case_id": str(updated_case["_id"]),
            "old_status": existing_case["status"],
            "new_status": new_status.value
        }
    )

    return updated_case





def assign_case_investigator(
    case_id: str,
    user_id: str,
    current_user: dict
):
    organization_id = get_organization_id(current_user)

    case = case_model.get_case_by_id(case_id, organization_id)

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    investigator = get_user_by_id_and_organization(
        user_id,
        organization_id
    )

    if not investigator:
        raise HTTPException(
            status_code=404,
            detail="Investigator not found in your organization"
        )

    if investigator.get("role") != "investigator":
        raise HTTPException(
            status_code=400,
            detail="Only investigators can be assigned"
        )

    if not investigator.get("is_active"):
        raise HTTPException(
            status_code=400,
            detail="Inactive users cannot be assigned"
        )

    updated_case = case_model.assign_investigator(
        case_id,
        organization_id,
        user_id
    )

    create_audit_log(
        actor_user_id=str(current_user["_id"]),
        action="case.investigator_assigned",
        target_user_id=user_id,
        organization_id=organization_id,
        changes={"case_id": case_id}
    )

    return updated_case


def remove_case_investigator(
    case_id: str,
    user_id: str,
    current_user: dict
):
    organization_id = get_organization_id(current_user)

    updated_case = case_model.remove_investigator(
        case_id,
        organization_id,
        user_id
    )

    if not updated_case:
        raise HTTPException(status_code=404, detail="Case not found")

    create_audit_log(
        actor_user_id=str(current_user["_id"]),
        action="case.investigator_removed",
        target_user_id=user_id,
        organization_id=organization_id,
        changes={"case_id": case_id}
    )

    return updated_case


def close_case(case_id: str, current_user: dict):
    """Close a case belonging to the user's organization."""

    organization_id = get_organization_id(current_user)

    existing_case = case_model.get_case_by_id(
        case_id,
        organization_id
    )

    if not existing_case:
        raise HTTPException(
            status_code=404,
            detail="Case not found"
        )

    if existing_case.get("is_archived", False):
        raise HTTPException(
            status_code=400,
            detail="Archived cases cannot be modified"
        )

    if existing_case["status"] == CaseStatus.CLOSED.value:
        raise HTTPException(
            status_code=400,
            detail="Case is already closed"
        )

    updated_case = case_model.update_case(
        case_id,
        organization_id,
        {"status": CaseStatus.CLOSED.value}
    )

    create_audit_log(
        actor_user_id=str(current_user["_id"]),
        action="case.closed",
        target_user_id=None,
        organization_id=organization_id,
        changes={
            "case_id": str(updated_case["_id"]),
            "previous_status": existing_case["status"],
            "new_status": "closed"
        }
    )

    return updated_case


def archive_existing_case(case_id: str, current_user: dict):
    """Archive a closed case."""

    organization_id = get_organization_id(current_user)

    archived_case = case_model.archive_case(
        case_id=case_id,
        organization_id=organization_id,
        archived_by=str(current_user["_id"])
    )

    if not archived_case:
        raise HTTPException(
            status_code=400,
            detail="Case not found, already archived, or not closed"
        )

    create_audit_log(
        actor_user_id=str(current_user["_id"]),
        action="case.archived",
        target_user_id=None,
        organization_id=organization_id,
        changes={
            "case_id": str(archived_case["_id"]),
            "case_number": archived_case["case_number"]
        }
    )

    return archived_case


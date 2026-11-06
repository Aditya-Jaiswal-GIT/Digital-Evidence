
from fastapi import APIRouter, Depends, status,Query

from app.schemas.case_schema import (
    CaseCreateRequest,
    CaseResponse,
     CaseListResponse,
     CaseUpdateRequest,
     CaseStatusUpdateRequest
)

from app.services.case_service import(
     create_new_case,
     get_all_cases, 
     get_single_case,
     update_case_details,
     update_case_status,
     assign_case_investigator,
     remove_case_investigator,
     close_case,
     archive_existing_case
     )

from app.core.dependencies import (
    get_current_user,
    require_permissions
)

from app.core.permissions import Permission

from bson import ObjectId
from app.schemas.case_assignment_schema import AssignInvestigatorRequest
from app.core.permissions import Permission

router = APIRouter(
    prefix="/cases",
    tags=["Case Management"]
)


@router.post(
    "/",
    response_model=CaseResponse,
    status_code=status.HTTP_201_CREATED
)
def create_case(
    case_data: CaseCreateRequest,
    current_user: dict = Depends(
        require_permissions(Permission.CREATE_CASE)
    )
):
    """Create a new forensic case."""

    created_case = create_new_case(
        case_data.model_dump(),
        current_user
    )

    return {
        "id": str(created_case["_id"]),
        "case_number": created_case["case_number"],
        "title": created_case["title"],
        "description": created_case["description"],
        "case_type": created_case["case_type"],
        "status": created_case["status"],
        "priority": created_case["priority"],
        "organization_id": str(created_case["organization_id"]),
        "created_by": str(created_case["created_by"]),
        "assigned_investigators": [
            str(user_id)
            for user_id in created_case["assigned_investigators"]
        ],
        "created_at": created_case["created_at"],
        "updated_at": created_case["updated_at"]
    }

@router.get(
    "/",
    response_model=CaseListResponse
)
def list_cases(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """List cases belonging to the current user's organization."""

    result = get_all_cases(
        current_user=current_user,
        page=page,
        page_size=page_size
    )

    return {
        "cases": [
            {
                "id": str(case["_id"]),
                "case_number": case["case_number"],
                "title": case["title"],
                "description": case["description"],
                "case_type": case["case_type"],
                "status": case["status"],
                "priority": case["priority"],
                "organization_id": str(case["organization_id"]),
                "created_by": str(case["created_by"]),
                "assigned_investigators": [
                    str(user_id)
                    for user_id in case.get("assigned_investigators", [])
                ],
                "created_at": case["created_at"],
                "updated_at": case["updated_at"]
            }
            for case in result["cases"]
        ],
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"]
    }


@router.get(
    "/{case_id}",
    response_model=CaseResponse
)
def view_case(
    case_id: str,
    current_user: dict = Depends(get_current_user)
):
    """View an individual case."""

    case = get_single_case(
        case_id=case_id,
        current_user=current_user
    )

    return {
        "id": str(case["_id"]),
        "case_number": case["case_number"],
        "title": case["title"],
        "description": case["description"],
        "case_type": case["case_type"],
        "status": case["status"],
        "priority": case["priority"],
        "organization_id": str(case["organization_id"]),
        "created_by": str(case["created_by"]),
        "assigned_investigators": [
            str(user_id)
            for user_id in case.get("assigned_investigators", [])
        ],
        "created_at": case["created_at"],
        "updated_at": case["updated_at"]
    }


def serialize_case(case: dict):
    return {
        "id": str(case["_id"]),
        "case_number": case["case_number"],
        "title": case["title"],
        "description": case["description"],
        "case_type": case["case_type"],
        "status": case["status"],
        "priority": case["priority"],
        "organization_id": str(case["organization_id"]),
        "created_by": str(case["created_by"]),
        "assigned_investigators": [
            str(user_id)
            for user_id in case.get("assigned_investigators", [])
        ],
        "created_at": case["created_at"],
        "updated_at": case["updated_at"]
    }



@router.patch("/{case_id}", response_model=CaseResponse)
def update_case(
    case_id: str,
    case_data: CaseUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    updated_case = update_case_details(
        case_id=case_id,
        update_data=case_data.model_dump(exclude_unset=True),
        current_user=current_user
    )

    return serialize_case(updated_case)


@router.patch("/{case_id}/status", response_model=CaseResponse)
def change_case_status(
    case_id: str,
    status_data: CaseStatusUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    updated_case = update_case_status(
        case_id=case_id,
        new_status=status_data.status,
        current_user=current_user
    )

    return serialize_case(updated_case)



@router.post("/{case_id}/assign", response_model=CaseResponse)
def assign_investigator_to_case(
    case_id: str,
    request: AssignInvestigatorRequest,
    current_user: dict = Depends(
        require_permissions(Permission.MANAGE_USERS)
    )
):
    case = assign_case_investigator(
        case_id,
        request.user_id,
        current_user
    )

    return serialize_case(case)


@router.delete("/{case_id}/assign/{user_id}", response_model=CaseResponse)
def remove_investigator_from_case(
    case_id: str,
    user_id: str,
    current_user: dict = Depends(
        require_permissions(Permission.MANAGE_USERS)
    )
):
    case = remove_case_investigator(
        case_id,
        user_id,
        current_user
    )

    return serialize_case(case)


@router.get("/{case_id}/investigators")
def get_case_investigators(
    case_id: str,
    current_user: dict = Depends(get_current_user)
):
    case = get_single_case(
        case_id=case_id,
        current_user=current_user
    )

    return {
        "case_id": str(case["_id"]),
        "case_number": case["case_number"],
        "assigned_investigators": [
            str(user_id)
            for user_id in case.get("assigned_investigators", [])
        ],
        "total": len(case.get("assigned_investigators", []))
    }



@router.patch("/{case_id}/close", response_model=CaseResponse)
def close_case_endpoint(
    case_id: str,
    current_user: dict = Depends(
        require_permissions(Permission.MANAGE_USERS)
    )
):
    case = close_case(
        case_id=case_id,
        current_user=current_user
    )

    return serialize_case(case)


@router.patch("/{case_id}/archive")
def archive_case_endpoint(
    case_id: str,
    current_user: dict = Depends(
        require_permissions(Permission.MANAGE_USERS)
    )
):
    case = archive_existing_case(
        case_id=case_id,
        current_user=current_user
    )

    return {
        "message": "Case archived successfully",
        "case_id": str(case["_id"]),
        "case_number": case["case_number"],
        "is_archived": case["is_archived"],
        "archived_at": case["archived_at"]
    }

from fastapi import APIRouter, Depends

from app.core.dependencies import (
    require_permissions
)

from app.core.permissions import Permission


router = APIRouter(
    prefix="/cases",
    tags=["Cases"]
)


@router.post("/")
def create_case(
    current_user: dict = Depends(
        require_permissions(Permission.CREATE_CASE)
    )
):

    return {
        "message": "Case creation authorized",
        "created_by": str(current_user["_id"])
    }

@router.post("/analysis/run")
def run_analysis(
    current_user: dict = Depends(
        require_permissions(Permission.RUN_ANALYSIS)
    )
):

    return {
        "message": "Analysis permission granted"
    }

@router.post("/findings/review")
def review_findings(
    current_user: dict = Depends(
        require_permissions(Permission.REVIEW_FINDINGS)
    )
):

    return {
        "message": "Review permission granted"
    }
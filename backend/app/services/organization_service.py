from fastapi import HTTPException, status

from app.models.organization_model import (
    create_organization,
    get_organization_by_name
)


def register_organization(name: str, description: str = ""):
    name = " ".join(name.split())

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Organization name cannot be empty"
        )

    existing = get_organization_by_name(name)

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Organization already exists"
        )

    try:
        organization_id = create_organization(
            name=name,
            description=description
        )
    except Exception:
        raise HTTPException(
            status_code=409,
            detail="Could not create organization"
        )

    return {
        "id": organization_id,
        "name": name,
        "description": description,
        "is_active": True
    }
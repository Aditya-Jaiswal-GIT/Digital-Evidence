from datetime import datetime, timezone

from app.core.database import database


audit_collection = database["audit_logs"]


def create_audit_log(
    actor_user_id: str,
    action: str,
    target_user_id: str,
    changes: dict,
    organization_id: str | None = None
):
    audit_document = {
        "actor_user_id": actor_user_id,
        "action": action,
        "target_user_id": target_user_id,
        "organization_id": organization_id,
        "changes": changes,
        "created_at": datetime.now(timezone.utc)
    }

    result = audit_collection.insert_one(audit_document)

    return str(result.inserted_id)
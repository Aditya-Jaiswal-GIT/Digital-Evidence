from app.core.database import database
from app.models.audit_model import audit_collection

from app.models.organization_model import organizations_collection


def initialize_database():

    # Users
    database.users.create_index(
        "email",
        unique=True
    )

    # Organizations
    database.organizations.create_index(
        "organization_id",
        unique=True
    )

    # Cases
    database.cases.create_index(
        [("organization_id", 1), ("case_number", 1)],
        unique=True
    )

    # Evidence
    database.evidence.create_index("case_id")
    database.evidence.create_index("integrity.original_hash")

    # Analysis jobs
    database.analysis_jobs.create_index(
        "job_id",
        unique=True
    )
    database.analysis_jobs.create_index(
        [("evidence_id", 1), ("status", 1)]
    )

    # Analysis results
    database.analysis_results.create_index("evidence_id")

    # Findings
    database.findings.create_index("result_id")

    # Chain of custody
    database.custody_events.create_index(
        [("evidence_id", 1), ("timestamp", 1)]
    )

    # Reports
    database.reports.create_index("case_id")

    # Audit logs
    database.audit_logs.create_index(
        [("organization_id", 1), ("timestamp", -1)]
    )

    database.refresh_tokens.create_index(
    "token_hash",
    unique=True
)

    database.refresh_tokens.create_index(
    "expires_at",
    expireAfterSeconds=0
)

    print("Database collections and indexes initialized!")




audit_collection.create_index(
    [("actor_user_id", 1), ("created_at", -1)]
)

audit_collection.create_index(
    [("target_user_id", 1), ("created_at", -1)]
)

audit_collection.create_index(
    [("action", 1), ("created_at", -1)]
)
organizations_collection.create_index(
    "name",
    unique=True
)
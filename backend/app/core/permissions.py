from enum import Enum


class Role(str, Enum):

    ADMIN = "admin"
    INVESTIGATOR = "investigator"
    FORENSIC_ANALYST = "forensic_analyst"
    REVIEWER = "reviewer"


class Permission(str, Enum):

    MANAGE_USERS = "manage_users"
    MANAGE_ORGANIZATIONS = "manage_organizations"

    CREATE_CASE = "create_case"
    UPLOAD_EVIDENCE = "upload_evidence"

    VIEW_EVIDENCE = "view_evidence"

    RUN_ANALYSIS = "run_analysis"

    VIEW_FINDINGS = "view_findings"
    REVIEW_FINDINGS = "review_findings"

    GENERATE_REPORT = "generate_report"


ROLE_PERMISSIONS = {

    Role.ADMIN: {
        Permission.MANAGE_USERS,
        Permission.MANAGE_ORGANIZATIONS,
        Permission.CREATE_CASE,
        Permission.UPLOAD_EVIDENCE,
        Permission.VIEW_EVIDENCE,
        Permission.RUN_ANALYSIS,
        Permission.VIEW_FINDINGS,
        Permission.REVIEW_FINDINGS,
        Permission.GENERATE_REPORT
    },

    Role.INVESTIGATOR: {
        Permission.CREATE_CASE,
        Permission.UPLOAD_EVIDENCE,
        Permission.VIEW_EVIDENCE,
        Permission.VIEW_FINDINGS
    },

    Role.FORENSIC_ANALYST: {
        Permission.VIEW_EVIDENCE,
        Permission.RUN_ANALYSIS,
        Permission.VIEW_FINDINGS
    },

    Role.REVIEWER: {
        Permission.VIEW_EVIDENCE,
        Permission.VIEW_FINDINGS,
        Permission.REVIEW_FINDINGS
    }

}
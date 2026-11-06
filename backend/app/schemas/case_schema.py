
from enum import Enum
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


# Case status
class CaseStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    CLOSED = "closed"


# Case priority
class CasePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Create case request
class CaseCreateRequest(BaseModel):
    title: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=10, max_length=2000)
    case_type: str = Field(min_length=3, max_length=100)
    priority: CasePriority = CasePriority.MEDIUM

    model_config = ConfigDict(extra="forbid")


# Update case request
class CaseUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=5, max_length=200)
    description: str | None = Field(default=None, min_length=10, max_length=2000)
    case_type: str | None = Field(default=None, min_length=3, max_length=100)
    priority: CasePriority | None = None

    model_config = ConfigDict(extra="forbid")


# Case response
class CaseResponse(BaseModel):
    id: str
    case_number: str
    title: str
    description: str
    case_type: str
    status: CaseStatus
    priority: CasePriority
    organization_id: str
    created_by: str
    assigned_investigators: list[str] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(extra="ignore")


# Case list response
class CaseListResponse(BaseModel):
    cases: list[CaseResponse]
    total: int
    page: int
    page_size: int



class CaseStatusUpdateRequest(BaseModel):
    status: CaseStatus

    model_config = ConfigDict(extra="forbid")

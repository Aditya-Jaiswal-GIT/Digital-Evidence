
from pydantic import BaseModel, Field, ConfigDict


class AssignInvestigatorRequest(BaseModel):
    user_id: str = Field(min_length=24, max_length=24)

    model_config = ConfigDict(extra="forbid")

from typing import List, Literal, Optional, Union
from pydantic import BaseModel

PipelineStatus = Literal["SUCCESS", "PARTIAL", "FAILED"]
ArtifactStatus = Literal["GENERATED", "SKIPPED", "FAILED"]

class ArtifactResult(BaseModel):
    name: str
    required: bool
    status: ArtifactStatus
    error: Optional[str] = None

class PipelineRunResult(BaseModel):
    status: PipelineStatus
    project_id: str
    personas_selected: int
    artifacts: List[ArtifactResult]
    blocking_errors: List[str]
    logs: List[str] = []

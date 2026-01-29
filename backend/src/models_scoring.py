from pydantic import BaseModel, ConfigDict
from typing import Dict, Optional, Any

class ValidationResult(BaseModel):
    is_valid: bool
    status_code: str # "OK", "INVALID_SCHEMA", "INVALID_LOGIC", "DUPLICATE"
    errors: list[str] = []

class ScoreBreakdown(BaseModel):
    objective_fit: float
    price_fit: float
    geography_fit: float
    funnel_fit: float
    ads_feasibility: float
    
    # Allow extra fields/metadata if needed but standardizing on these for now
    model_config = ConfigDict(extra='ignore')

class ScoredPersona(BaseModel):
    persona_id: str
    total_score: float
    score_breakdown: ScoreBreakdown
    rank: Optional[int] = None
    reasoning: Optional[str] = None
    project_id: str

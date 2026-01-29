from pydantic import BaseModel
from typing import List, Dict, Optional, Literal

class ScalingRule(BaseModel):
    name: str # e.g. "Scale Up Winner"
    condition: str # e.g. "CPA < target AND spend > 3x daily"
    action: str # e.g. "+20%"
    trigger_type: Literal["Scale Up", "Kill", "Hold"]

class BudgetAllocation(BaseModel):
    persona_id: str
    project_id: str
    total_daily_budget: float
    meta_budget: float
    google_budget: float
    
class FunnelSplit(BaseModel):
    structure_type: str # e.g. "Meta Adset" or "Google AdGroup"
    name: str 
    funnel_stage: str # TOF, MOF, BOF
    alloc_percentage: float
    daily_budget: float

class BudgetPlan(BaseModel):
    project_id: str
    total_budget: float
    allocations: List[BudgetAllocation]
    funnel_splits: Dict[str, List[FunnelSplit]] # Keyed by persona_id
    rules: List[ScalingRule]
    rationale: Optional[str] = None

